
import sys

def main():
    try:
        if len(sys.argv) != 1:
            print("Bad program call.")
            return -1

        print(f"arg 0 {sys.argv[0]}")
        #client.run()

        return 0

    except Exception as err:
        print(f"Something went wrong and an exception was caught: {str(err)}")
        return -1

if __name__ == '__main__':
    sys.exit(main())
