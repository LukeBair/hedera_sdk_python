import re

from src.hedera_sdk_python.hapi.services import basic_types_pb2
from src.hedera_sdk_python.tokens.token_id import TokenId

class NftId:
    def __init__(self, token_id=None, serial_number=0):
        if token_id is None:
            raise TypeError("token_id is required")
        if not isinstance(token_id, TokenId):
            raise TypeError(f"token_id must be of type TokenId, got {type(token_id)}")
        if not isinstance(serial_number, int):
            raise TypeError(f"Expected an integer for serial_number, got {type(serial_number)}")
        if serial_number < 0:
            raise ValueError("serial_number must be positive")

        self.tokenId = token_id
        self.serialNumber = serial_number

    # NOTE: there is a validate function in the go sdk,
    #  also some validate checksums (???) in others not mentioned
    #  in the protobuf or hedera docs, this may be misleading
    def is_valid(self):
        if self.tokenId is None:
            raise TypeError("token_id is required")
        if not isinstance(self.tokenId, TokenId):
            raise TypeError(f"token_id must be of type TokenId, got {type(self.tokenId)}")
        if not isinstance(self.serialNumber, int):
            raise TypeError(f"Expected an integer for serial_number, got {type(self.serialNumber)}")
        if self.serialNumber < 0:
            raise ValueError("serial_number must be positive")
        return True

    @classmethod
    def from_proto(cls, nft_id_proto = None):
        """
        :param nft_id_proto: the proto NftID object
        :return: a NftId object
        """
        if nft_id_proto is None:
            raise ValueError("nft_id_proto is required")
        elif not isinstance(nft_id_proto, basic_types_pb2.NftID):
            raise TypeError("nft_id_proto must be of type NftID\n(src.hedera_sdk_python.hapi.services.basic_types_pb2.NftID)")

        return cls(
            token_id=TokenId.from_proto(nft_id_proto.token_ID),
            serial_number=nft_id_proto.serial_number
        )

    def to_proto(self):
        """
        :return: a protobuf NftID object representation of this NftId object
        """
        self.is_valid()
        nft_id_proto = basic_types_pb2.NftID(token_ID=self.tokenId.to_proto(), serial_number=self.serialNumber)

        return nft_id_proto

    @classmethod
    def from_string(cls, nft_id_str = ""):
        """
        :param nft_id_str: a string NftId representation
        :return: returns the NftId parsed from the string input
        """
        if nft_id_str == "":
            raise ValueError("nft_id_str cannot be empty")
        elif not isinstance(nft_id_str, str):
            raise TypeError("nft_id_str must be of type string")

        parts = re.split(r"/", nft_id_str)
        if len(parts) != 2:
            raise ValueError("nft_id_str must formatted as: shard.realm.number/serial_number")

        return cls(
            token_id=TokenId.from_string(parts[0]),
            serial_number=int(parts[1])
        )

    def __str__(self):
        """
        :return: a human-readable representation of the NftId
        """
        self.is_valid()
        return f"{str(self.tokenId)}/{str(self.serialNumber)}"

    def __repr__(self):
        """
        :return: a string representation of the NftId
        """
        self.is_valid()
        return f"NftId({str(self)})"

    # NOTE: TokenId did not have an __eq__ method, added one
    #
    # NOTE: Not sure if I should be checking for is_valid() everywhere
    #  but its probably not a bad idea
    def __eq__(self, other):
        """
        :param other: The other NftId object
        :return: Does this NftId object have identical TokenId's and Serial Numbers?
        """
        self.is_valid()
        if not isinstance(other, NftId):
            return False
        else:
            other.is_valid()

        if self.serialNumber != other.serialNumber:
            return False
        elif self.tokenId != other.tokenId:
            return False
        return True