from google import Google

def download():
    search_query = input("What are you searching for? ")
    limit = input("Maximum number of images: ")
    limit = int(limit)
    google = Google(search_query,limit)
    google.run()

if __name__ == '__main__':
    download()
