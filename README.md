# Telegram message capture + Sending to broker Quotex
## Telegram message capture + Sending to broker Quotex

Install these dependencies

```plaintext
pip install pytz
pip install telethon
```

Install these quotexAPI dependencies

**Copyright**: https://github.com/cleitonleonel/pyquotex

```plaintext
pip install -r requirements.txt
```

Execute **id\_chat\_group\_telegram.py** to obtain the chat and/or telegram group IDs.

@@ -11,8 +26,12 @@ Create a **.env** with these properties
```javascript
API_ID=id-api-telegram
API_HASH=hash-api-telegram
PHONE_NUMBER=example(+51999888777)
PHONE_NUMBER=+51999888777
ID_GRUPO_CHAT=obtain-execute-id_chat_group_telegram.py
CORREO=email-account-quotex
PASSWORD=password-account-quotex
```

More information

https://github.com/cleitonleonel/pyquotex
