def fake_translate(text:str, from_lang:str, to_lang:str)->str:
    pairs={
        ("en","es"):"Hola a todos, bienvenidos a nuestra demo.",
        ("en","fr"):"Bonjour à tous, bienvenue à notre démonstration.",
        ("es","en"):"Hello everyone, welcome to our demo.",
        ("fr","en"):"Hello everyone, welcome to our demo.",
    }
    return pairs.get((from_lang,to_lang), f"({to_lang}) {text}")
