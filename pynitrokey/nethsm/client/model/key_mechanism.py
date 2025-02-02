# coding: utf-8

"""
    NetHSM

    All endpoints expect exactly the specified JSON. Additional properties will cause a Bad Request Error (400). All HTTP errors contain a JSON structure with an explanation of type string. All <a href=\"https://tools.ietf.org/html/rfc4648#section-4\">base64</a> encoded values are Big Endian.  # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""

from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401

import frozendict  # noqa: F401

from pynitrokey.nethsm.client import schemas  # noqa: F401


class KeyMechanism(
    schemas.EnumBase,
    schemas.StrSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        enum_value_to_name = {
            "RSA_Decryption_RAW": "RSA_DECRYPTION_RAW",
            "RSA_Decryption_PKCS1": "RSA_DECRYPTION_PKCS1",
            "RSA_Decryption_OAEP_MD5": "RSA_DECRYPTION_OAEP_MD5",
            "RSA_Decryption_OAEP_SHA1": "RSA_DECRYPTION_OAEP_SHA1",
            "RSA_Decryption_OAEP_SHA224": "RSA_DECRYPTION_OAEP_SHA224",
            "RSA_Decryption_OAEP_SHA256": "RSA_DECRYPTION_OAEP_SHA256",
            "RSA_Decryption_OAEP_SHA384": "RSA_DECRYPTION_OAEP_SHA384",
            "RSA_Decryption_OAEP_SHA512": "RSA_DECRYPTION_OAEP_SHA512",
            "RSA_Signature_PKCS1": "RSA_SIGNATURE_PKCS1",
            "RSA_Signature_PSS_MD5": "RSA_SIGNATURE_PSS_MD5",
            "RSA_Signature_PSS_SHA1": "RSA_SIGNATURE_PSS_SHA1",
            "RSA_Signature_PSS_SHA224": "RSA_SIGNATURE_PSS_SHA224",
            "RSA_Signature_PSS_SHA256": "RSA_SIGNATURE_PSS_SHA256",
            "RSA_Signature_PSS_SHA384": "RSA_SIGNATURE_PSS_SHA384",
            "RSA_Signature_PSS_SHA512": "RSA_SIGNATURE_PSS_SHA512",
            "EdDSA_Signature": "ED_DSA_SIGNATURE",
            "ECDSA_Signature": "ECDSA_SIGNATURE",
            "AES_Encryption_CBC": "AES_ENCRYPTION_CBC",
            "AES_Decryption_CBC": "AES_DECRYPTION_CBC",
        }
    
    @schemas.classproperty
    def RSA_DECRYPTION_RAW(cls):
        return cls("RSA_Decryption_RAW")
    
    @schemas.classproperty
    def RSA_DECRYPTION_PKCS1(cls):
        return cls("RSA_Decryption_PKCS1")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_MD5(cls):
        return cls("RSA_Decryption_OAEP_MD5")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_SHA1(cls):
        return cls("RSA_Decryption_OAEP_SHA1")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_SHA224(cls):
        return cls("RSA_Decryption_OAEP_SHA224")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_SHA256(cls):
        return cls("RSA_Decryption_OAEP_SHA256")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_SHA384(cls):
        return cls("RSA_Decryption_OAEP_SHA384")
    
    @schemas.classproperty
    def RSA_DECRYPTION_OAEP_SHA512(cls):
        return cls("RSA_Decryption_OAEP_SHA512")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PKCS1(cls):
        return cls("RSA_Signature_PKCS1")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_MD5(cls):
        return cls("RSA_Signature_PSS_MD5")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_SHA1(cls):
        return cls("RSA_Signature_PSS_SHA1")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_SHA224(cls):
        return cls("RSA_Signature_PSS_SHA224")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_SHA256(cls):
        return cls("RSA_Signature_PSS_SHA256")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_SHA384(cls):
        return cls("RSA_Signature_PSS_SHA384")
    
    @schemas.classproperty
    def RSA_SIGNATURE_PSS_SHA512(cls):
        return cls("RSA_Signature_PSS_SHA512")
    
    @schemas.classproperty
    def ED_DSA_SIGNATURE(cls):
        return cls("EdDSA_Signature")
    
    @schemas.classproperty
    def ECDSA_SIGNATURE(cls):
        return cls("ECDSA_Signature")
    
    @schemas.classproperty
    def AES_ENCRYPTION_CBC(cls):
        return cls("AES_Encryption_CBC")
    
    @schemas.classproperty
    def AES_DECRYPTION_CBC(cls):
        return cls("AES_Decryption_CBC")
