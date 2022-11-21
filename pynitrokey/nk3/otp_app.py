"""
Oath Authenticator client

Used through CTAPHID transport, via the custom vendor command.
Can be used directly over CCID as well.
"""
import logging
import typing
from enum import Enum
from struct import pack
from typing import List, Optional

import dataclasses
import tlv8

from pynitrokey.nk3 import Nitrokey3Device
from pynitrokey.start.gnuk_token import iso7816_compose


@dataclasses.dataclass
class RawBytes:
    data: List


@dataclasses.dataclass
class SelectResponse:
    version: bytes
    name: bytes
    challenge: Optional[bytes]
    algorithm: Optional[bytes]


class Instruction(Enum):
    Put = 0x1
    Delete = 0x2
    SetCode = 0x3
    Reset = 0x4
    List = 0xA1
    Calculate = 0xA2
    Validate = 0xA3
    CalculateAll = 0xA4
    SendRemaining = 0xA5
    VerifyCode = 0xB1
    Select = 0xA4


class Tag(Enum):
    CredentialId = 0x71
    NameList = 0x72
    Key = 0x73
    Challenge = 0x74
    Response = 0x75
    Properties = 0x78
    InitialCounter = 0x7A
    Version = 0x79
    Algorithm = 0x7B


class Kind(Enum):
    Hotp = 0x10
    Totp = 0x20
    HotpReverse = 0x30


STRING_TO_KIND = {
    "HOTP": Kind.Hotp,
    "TOTP": Kind.Totp,
    "HOTP_REVERSE": Kind.HotpReverse,
}


class Algorithm(Enum):
    Sha1 = 0x01
    Sha256 = 0x02
    Sha512 = 0x03


class OTPApp:
    """
    This is an Oath Authenticator client
    """

    log: logging.Logger
    logfn: typing.Callable
    dev: Nitrokey3Device

    def __init__(self, dev: Nitrokey3Device, logfn: Optional[typing.Callable] = None):
        self.log = logging.getLogger("otpapp")
        if logfn is not None:
            self.logfn = logfn  # type: ignore [assignment]
        else:
            self.logfn = self.log.info  # type: ignore [assignment]
        self.dev = dev

    def _custom_encode(self, structure: Optional[List] = None) -> bytes:
        if not structure:
            return b""

        def transform(d: typing.Union[tlv8.Entry, RawBytes, None]) -> bytes:
            if not d:
                return b""
            if isinstance(d, RawBytes):
                # return b"".join(d.data)
                return bytes(d.data)
            if isinstance(d, tlv8.Entry):
                return tlv8.encode([d])
            return b""

        encoded_structure = b"".join(map(transform, structure))
        return encoded_structure

    def _send_receive(
        self, ins: Instruction, structure: Optional[List] = None
    ) -> bytes:
        encoded_structure = self._custom_encode(structure)
        ins_b, p1, p2 = self._encode_command(ins)
        bytes_data = iso7816_compose(ins_b, p1, p2, data=encoded_structure)
        return self._send_receive_inner(bytes_data)

    def _send_receive_inner(self, data: bytes) -> bytes:
        self.logfn(f"Sending {data.hex() if data else data!r}")

        try:
            result = self.dev.otp(data=data)
        except Exception as e:
            self.logfn(f"Got exception: {e}")
            raise

        self.logfn(f"Received {result.hex() if data else data!r}")
        return result

    @classmethod
    def _encode_command(cls, command: Instruction) -> bytes:
        p1 = 0
        p2 = 0
        if command == Instruction.Reset:
            p1 = 0xDE
            p2 = 0xAD
        elif command == Instruction.Select:
            p1 = 0x04
            p2 = 0x00
        elif command == Instruction.Calculate or command == Instruction.CalculateAll:
            p1 = 0x00
            p2 = 0x01
        return bytes([command.value, p1, p2])

    def reset(self) -> None:
        """
        Remove all credentials from the database
        """
        self.logfn("Executing reset")
        self._send_receive(Instruction.Reset)

    def list(self) -> List[bytes]:
        """
        Return a list of the registered credentials
        :return: List of bytestrings
        """
        raw_res = self._send_receive(Instruction.List)
        resd: tlv8.EntryList = tlv8.decode(raw_res)
        res = []
        for e in resd:
            # e: tlv8.Entry
            res.append(e.data[1:])
        return res

    def delete(self, cred_id: bytes) -> None:
        """
        Delete credential with the given id. Does not fail, if the given credential does not exist.
        :param credid: Credential ID
        """
        structure = [
            tlv8.Entry(Tag.CredentialId.value, cred_id),
        ]
        self._send_receive(Instruction.Delete, structure)

    def register(
        self,
        credid: bytes,
        secret: bytes,
        digits: int,
        kind: Kind = Kind.Hotp,
        algo: Algorithm = Algorithm.Sha1,
        initial_counter_value: int = 0,
        touch_button_required: bool = False,
    ) -> None:
        """
        Register new OTP credential
        :param credid: Credential ID
        :param secret: The shared key
        :param digits: Digits of the produced code
        :param kind: OTP variant - HOTP or TOTP
        :param algo: The hash algorithm to use - SHA1, SHA256 or SHA512
        :param initial_counter_value: The counter's initial value for the HOTP credential (HOTP only)
        :param touch_button_required: User Presence confirmation is required to use this Credential
        :return: None
        """
        if initial_counter_value > 0xFFFFFFFF:
            raise Exception("Initial counter value must be smaller than 4 bytes")
        if algo == Algorithm.Sha512:
            raise NotImplementedError(
                "This hash algorithm is not supported by the firmware"
            )

        self.logfn(
            f"Setting new credential: {credid!r}, {secret.hex()}, {kind}, {algo}, counter: {initial_counter_value}"
        )

        structure = [
            tlv8.Entry(Tag.CredentialId.value, credid),
            # header (2) + secret (N)
            tlv8.Entry(
                Tag.Key.value, bytes([kind.value | algo.value, digits]) + secret
            ),
            RawBytes([Tag.Properties.value, 0x02 if touch_button_required else 0x00]),
            tlv8.Entry(
                Tag.InitialCounter.value, initial_counter_value.to_bytes(4, "big")
            ),
        ]
        self._send_receive(Instruction.Put, structure)

    def calculate(self, cred_id: bytes, challenge: int) -> bytes:
        """
        Calculate the OTP code for the credential named `cred_id`, and with challenge `challenge`.
        :param cred_id: The name of the credential
        :param challenge: Challenge for the calculations (TOTP only).
            Should be equal to: timestamp/period. The commonly used period value is 30.
        :return: OTP code as a byte string
        """
        structure = [
            tlv8.Entry(Tag.CredentialId.value, cred_id),
            tlv8.Entry(Tag.Challenge.value, pack(">Q", challenge)),
        ]
        res = self._send_receive(Instruction.Calculate, structure=structure)
        header = res[:2]
        assert header.hex() in ["7605", "7700"]
        digits = res[2]
        digest = res[3:]
        truncated_code = int.from_bytes(digest, byteorder="big", signed=False)
        code = (truncated_code & 0x7FFFFFFF) % pow(10, digits)
        codes: bytes = str(code).zfill(digits).encode()
        self.logfn(
            f"Received digest: {digest.hex()}, for challenge {challenge}, digits: {digits}, truncated code: {truncated_code!r}, pre-code: {code!r},"
            f" final code: {codes!r}"
        )
        return codes

    def verify_code(self, cred_id: bytes, code: int) -> bool:
        """
        Proceed with the incoming OTP code verification (aka reverse HOTP).
        :param cred_id: The name of the credential
        :param code: The HOTP code to verify. u32 representation.
        :return: fails with CTAP1 error; returns True if code matches the value calculated internally.
        """
        structure = [
            tlv8.Entry(Tag.CredentialId.value, cred_id),
            tlv8.Entry(Tag.Response.value, pack(">L", code)),
        ]
        res = self._send_receive(Instruction.VerifyCode, structure=structure)
        return res.hex() == "7700"

    def set_code(self, key: bytes, challenge: bytes, response: bytes) -> None:
        """
        Set code
        :param key:
        :param challenge:
        :param response:
        :return:
        """
        algo = Algorithm.Sha1.value
        kind = Kind.Totp.value
        structure = [
            tlv8.Entry(Tag.Key.value, bytes([kind | algo]) + key),
            tlv8.Entry(Tag.Challenge.value, challenge),
            tlv8.Entry(Tag.Response.value, response),
        ]
        self._send_receive(Instruction.SetCode, structure=structure)

    def validate(self, challenge: bytes, response: bytes) -> bytes:
        """
        Validate
        :param challenge:
        :param response:
        :return:
        """
        structure = [
            tlv8.Entry(Tag.Response.value, response),
            tlv8.Entry(Tag.Challenge.value, challenge),
        ]
        raw_res = self._send_receive(Instruction.Validate, structure=structure)
        resd: tlv8.EntryList = tlv8.decode(raw_res)
        return resd.data

    def select(self) -> SelectResponse:
        AID = [0xA0, 0x00, 0x00, 0x05, 0x27, 0x21, 0x01]
        structure = [RawBytes(AID)]
        raw_res = self._send_receive(Instruction.Select, structure=structure)
        resd: tlv8.EntryList = tlv8.decode(raw_res)
        rd = {}
        for e in resd:
            e: tlv8.Entry
            rd[e.type_id] = e.data

        r = SelectResponse(
            version=rd[Tag.Version.value],
            name=rd[Tag.CredentialId.value],
            challenge=rd.get(Tag.Challenge.value),
            algorithm=rd.get(Tag.Algorithm.value),
        )
        return r
