
from endee import Endee, Precision

try:
    print("Initializing Client...")
    client = Endee()
    print(f"Client type: {type(client)}")
    print(f"Client dir: {dir(client)}")

    # Mock index creation/retrieval
    index_name = "test_index"
    try:
        print(f"\nAttempting to get index '{index_name}'...")
        # We might not have a running server to connect to if we run this locally without settings
        # But let's see what get_index returns if we mock it or just check the class
        pass
    except Exception as e:
        print(f"Error getting index: {e}")

    # Inspect Endee class directly just in case
    import inspect
    print("\nEndee methods:")
    for name, method in inspect.getmembers(Endee):
        if not name.startswith("_"):
            print(name)

except Exception as e:
    print(f"General Error: {e}")
