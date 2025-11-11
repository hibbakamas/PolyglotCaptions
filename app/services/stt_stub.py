def fake_stt(_:bytes, from_lang:str)->str:
    samples={"en":"Hello everyone, welcome to our demo.",
             "es":"Hola a todos, bienvenidos a nuestra demo.",
             "fr":"Bonjour à tous, bienvenue à notre démonstration."}
    return samples.get(from_lang, samples["en"])

