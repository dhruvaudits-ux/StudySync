import urllib.request

def test_routes():
    base_url = "http://127.0.0.1:5000"
    routes = ["/dashboard", "/subjects", "/planner", "/activity"]
    
    for route in routes:
        try:
            # urllib.request.urlopen follows redirects by default, so we'll check the final URL
            response = urllib.request.urlopen(base_url + route)
            final_url = response.geturl()
            if "login" in final_url:
                print(f"Success: {route} is protected and redirected to login.")
            else:
                print(f"Failure: {route} did NOT redirect to login (ended at {final_url}).")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error for {route}: {e.code}")
        except Exception as e:
            print(f"Error testing {route}: {e}")

if __name__ == '__main__':
    test_routes()
