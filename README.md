# Opiskelijoiden-blogisivu
Sivulla pystyt:
- kirjoittamaan omaa blogia opiskeluun liittyvistä aiheista.
- seuraamaan muiden opiskelijoiden blogia
- hakea tiettyjä blogeja hausta
- kommentoida ja tykätä muista blogeista
- muokata oman profiilisi kuvaa ja nimeä.
- viestitellä muitten käyttäjien kanssa
- pystyt suodattamaan viestejä
- pitämään avointa keskustelua yllä, johon kaikki voivat osallistua
- (Ehkä myös pystyt vaihtamaan koko sivun teemaa (pimeäksi tai valoisaksi) ja muuta hassua mitä en oo viel keksiny)


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

