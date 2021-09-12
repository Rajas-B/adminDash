from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/user/account
def otp_auth(phone_number, otp):
    account_sid = "AC4678fe31a4598cd6f5cbd1c612830c98"
    auth_token = "2618652900d7a649711916d519f2a190"
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body=f'Verification of Phone number: {otp}',
            from_='+12016902258',
            to='+91' + phone_number,
        )
    print(message.sid)
