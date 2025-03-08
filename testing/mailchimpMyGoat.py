from mailchimp_marketing import Client

mailchimp = Client()
mailchimp.set_config({
  "api_key": "58d63b0d8745d5bad45f51d9eaecd283-us14",
  "server": "us14"
})

response = mailchimp.ping.get()
print(response)