def fake_translate(text: str, from_lang: str, to_lang: str) -> str:


   pairs = {
       ("en", "es"): "Hola a todos, bienvenidos a nuestra demo.",
       ("en", "fr"): "Bonjour à tous, bienvenue à notre démonstration.",
       ("es", "en"): "Hello everyone, welcome to our demo.",
       ("fr", "en"): "Hello everyone, welcome to our demo.",
   }


   key = (from_lang.lower(), to_lang.lower())
   if text.strip().lower() in ("hello everyone", "hello everyone, welcome to our demo"):
       # If they send a generic greeting, use the canned mapping
       canned = pairs.get(key)
       if canned:
           return canned


   # Fallback: just echo with language tag
   return f"[{to_lang}] {text}"