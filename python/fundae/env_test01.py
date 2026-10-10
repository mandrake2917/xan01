import requests

#---------------------------------------------------------------------------------------
# ReadMe:
# Remote Debugging (with frozen modules off)
# python3 -Xfrozen_modules=off -m debugpy --listen 5678 --wait-for-client env_test01.py 
# python3 -m debugpy --listen 5678 --wait-for-client env_test01.py 
#---------------------------------------------------------------------------------------

def fetch_joke():
    response = requests.get("https://api.chucknorris.io/jokes/random")
    if response.status_code == 200:
        data = response.json()
        print("Joke:", data["value"])
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    print("Starting Python script in VS Code...")
    fetch_joke()