# Opiskelijoiden-blogisivu
Sivulla pystyt:
- kirjoittamaan omaa blogia opiskeluun liittyvistä aiheista.
- lisäämään kuvia viesteihin ja blogipostauksiin.
- näkemään muiden blogit
- poistamaan omia blogipostauksia ja viestejä
- hakea tiettyjä blogeja hausta
- kommentoida ja tykätä muista blogeista
- viestitellä muitten käyttäjien kanssa
- pystyt suodattamaan viestejä
- pitämään avointa keskustelua yllä, johon kaikki voivat osallistua



#Avausohjeet.

# Opiskelijablogi


# Kloonaa GitHub-repo

1. git clone 
https://github.com/miltsii/Opiskelijoiden-blogisivu.git
2. cd Opiskelijoiden-blogisivu. 
3. Luo virtuaaliympäristö:  python3 -m venv venv
source venv/bin/activate
4. Kirjoita: pip install Flask
5. (Jos tarvitsee) Luo tietokanta: python -c "import sqlite3; conn = sqlite3.connect('database.db'); c = conn.cursor(); c.executescript(open('schema.sql').read()); conn.commit(); conn.close()"
6. Kirjoita "flask run"
7. http://127.0.0.1:5000

