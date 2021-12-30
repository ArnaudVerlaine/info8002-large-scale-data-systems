"""
User-level application (stub).
NB: Feel free to extend or modify.
"""

import argparse
from keychain import Storage
from time import sleep


def main(arguments):
    storage = allocate_application(arguments)
    response = None
    while True:
        response = input("""What do you want to do?
        1. PUT
        2. RETRIEVE
        3. RETRIEVE ALL
        4. Quit\n""")

        if response == "1":
            key = input("Key: introduce the key\n")
            value = input("Value: introduce the value\n")
            storage.put(key, value, block=False)
            #print(storage.get_chain())
        elif response == "2":
            key = input("Key: introduce the key to fetch\n")
            result = storage.retrieve(key)
            print(result)
        elif response == "3":
            key = input("Key: introduce the key to fetch\n")
            result = storage.retrieve_all(key)
            print(result)
        elif response == "4":
            print("Quitting...")
            storage.kill()
            break

    # Adding a key-value pair to the storage.

    #print(storage.get_chain())

    #callback = storage.put(key, value, block=False)

    # Depending on how fast your blockchain is,
    # this will return a proper result.
    #print(storage.retrieve(key))

    # Using the callback object,
    # you can also wait for the operation to be completed.
    #callback.wait()

    # Now the key should be available,
    # unless a different node `put` a new value.
    #print(storage.retrieve(key))

    # Show all values of the key.
    #print(storage.retrieve_all(key))


def allocate_application(arguments):
    application = Storage(
        bootstrap=arguments.bootstrap,
        miner=arguments.miner,
        difficulty=arguments.difficulty)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                            "an effect with the `--miner` flag has been set.")
    arguments, _ = parser.parse_known_args()

    return arguments


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)


