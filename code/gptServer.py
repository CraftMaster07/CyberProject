def get_content_type_from_request(http_request):
    # Split the HTTP request by lines
    lines = http_request.split('\n')
    
    # Find the line containing 'Accept' header
    accept_header = next((line for line in lines if line.startswith('Accept:')), None)
    
    if accept_header:
        # Extract the requested content types
        requested_content_types = accept_header.split(':')[1].strip().split(',')
        
        # Return the first requested content type
        return requested_content_types[0].strip()
        
    # If no 'Accept' header found, default to plain text
    return 'text/plain'

# Example HTTP request from browser
http_request = """GET /img/irene.jpg HTTP/1.1
Host: 127.0.0.1:8080
Connection: keep-alive
sec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
sec-ch-ua-platform: "Windows"
Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
Sec-GPC: 1
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: image
Referer: http://127.0.0.1:8080/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9,he;q=0.8
"""

# Test the function
content_type = get_content_type_from_request(http_request)
print("Content-Type to be sent in response:", content_type)