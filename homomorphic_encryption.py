import requests
from phe import paillier
from typing import List

URL = 'http://localhost'
PORT = '8000'
END_POINT = '/prediction'


def query_pred(input_vector: List[float]) -> int:

    # Generate key pair
    public_key, private_key = paillier.generate_paillier_keypair()

    # Encrypt input vector
    encrypted_number_list = [
        public_key.encrypt(x, precision=2**(-16)).ciphertext() for x in input_vector
    ]

    # Construct request data
    data = {
        'pub_key_n': public_key.n,
        'enc_feature_vector': encrypted_number_list
    }

    # Send POST request
    response = requests.post(URL + ':' + PORT + END_POINT, json=data)

    # Check response status code
    if response.status_code != 200:
        raise Exception(response.text)

    # Decrypt prediction
    raw_enc_prediction = response.json()['enc_prediction']
    enc_prediction = paillier.EncryptedNumber(
        public_key, raw_enc_prediction, exponent=-8)
    prediction = private_key.decrypt(enc_prediction)

    return prediction


def main():

    # Sample input vector
    input_vector = [0.48555949, 0.29289251, 0.63463107,
                    0.41933057, 0.78672205, 0.58910837,
                    0.00739207, 0.31390802, 0.37037496,
                    0.3375726]

    # Query prediction
    prediction = query_pred(input_vector)

    # Print prediction
    print(prediction)

    # Check prediction error
    assert 2**(-16) > abs(prediction - 0.44812144746653826)


if __name__ == "__main__":
    main()
