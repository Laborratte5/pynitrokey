# -*- coding: utf-8 -*-
#
# Copyright 2019 SoloKeys Developers
#
# Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
# http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
# http://opensource.org/licenses/MIT>, at your option. This file may not be
# copied, modified, or distributed except according to those terms.

import click
import json

import solo
import solo.operations
from solo.cli.key import key
from solo.cli.monitor import monitor
from solo.cli.program import program


@click.group()
def solo_cli():
    pass


solo_cli.add_command(key)
solo_cli.add_command(monitor)
solo_cli.add_command(program)


@click.command()
def version():
    """Version of python-solo library and tool."""
    print(solo.__version__)


solo_cli.add_command(version)


@click.command()
@click.option("--input-seed-file")
@click.argument("output_pem_file")
def genkey(input_seed_file, output_pem_file):
    """Generates key par that can be used for Solo signed firmware updates.

    \b
    * Generates NIST P256 keypair.
    * Public key must be copied into correct source location in solo bootloader
    * The private key can be used for signing updates.
    * You may optionally supply a file to seed the RNG for key generating.
    """

    vk = solo.operations.genkey(output_pem_file, input_seed_file=input_seed_file)

    print("Public key in various formats:")
    print()
    print([c for c in vk.to_string()])
    print()
    print("".join(["%02x" % c for c in vk.to_string()]))
    print()
    print('"\\x' + "\\x".join(["%02x" % c for c in vk.to_string()]) + '"')
    print()


solo_cli.add_command(genkey)


@click.command()
@click.argument("verifying-key")
@click.argument("app-hex")
@click.argument("output-json")
def sign(verifying_key, app_hex, output_json):
    """Signs a firmware hex file, outputs a .json file that can be used for signed update."""

    msg = solo.operations.sign_firmware(verifying_key, app_hex)
    print("Saving signed firmware to", output_json)
    with open(output_json, "wb+") as fh:
        fh.write(json.dumps(msg).encode())


solo_cli.add_command(sign)


@click.command()
@click.option("--attestation-key", help="attestation key in hex")
@click.argument("input_hex_files", nargs=-1)
@click.argument("output_hex_file")
def mergehex(attestation_key, input_hex_files, output_hex_file):
    """Merges hex files, and patches in the attestation key.

    \b
    If no attestation key is passed, uses default Solo Hacker one.
    Note that later hex files replace data of earlier ones, if they overlap.
    """
    solo.operations.mergehex(
        input_hex_files, output_hex_file, attestation_key=attestation_key
    )


solo_cli.add_command(mergehex)


@click.command()
def ls():
    """List Solos (in firmware or bootloader mode) and potential Solos in dfu mode."""

    solos = solo.client.find_all()
    print(":: Solos")
    for c in solos:
        descriptor = c.dev.descriptor
        print(f"{descriptor['path']}: {descriptor['product_string']}")

    st_dfus = solo.dfu.find_all()
    print(":: Potential Solos in DFU mode")
    for d in st_dfus:
        dev_raw = d.dev
        dfu_serial = dev_raw.serial_number
        print(f"{dfu_serial}")


solo_cli.add_command(ls)
