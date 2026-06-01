import discord
import requests
import json
import re
import base64
import hashlib
import random
import time
import urllib.parse
from discord import app_commands
from discord.ext import commands

TOKEN = "MTQ2MDM1MDQ5NDQ3NTAyNjcyMA.G74Fmi.zmeVnw1x-Qz_yCvPdtTgAqg4h6wqw_bQ4DE-yE"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ========== PROXY ET USER-AGENTS POUR CONTOURNEMENT ==========
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# ========== BASE DE DONNEES LEAKS (API publiques sans cle) ==========

# 1. API breachdirectory (gratuite, sans cle)
def search_breachdirectory(query):
    try:
        url = f"https://breachdirectory.org/api?breach=all&username={urllib.parse.quote(query)}"
        r = requests.get(url, headers=get_headers(), timeout=15)
        if r.status_code == 200:
            data = r.json()
            if 'result' in data and data['result']:
                return data['result']
        return []
    except:
        return []

# 2. API dehashed (simule via leakpeek - gratuit)
def search_dehashed(email):
    try:
        # Alternative gratuite a dehashed
        r = requests.get(f"https://leakpeek.com/api/email/{email}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# 3. API snusbase alternative (leakcheck gratuit)
def search_leakcheck(query):
    try:
        r = requests.get(f"https://leakcheck.net/api/public?check={query}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# 4. API haveibeenpwned (sans cle - rate limited)
def search_hibp(email):
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", 
                        headers={"hibp-api-key": "", "User-Agent": "osint-bot"}, timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# 5. API emailrep.io (gratuite, sans cle)
def search_emailrep(email):
    try:
        r = requests.get(f"https://emailrep.io/{email}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# 6. API whatsmyname (recherche username sur 400+ sites)
def search_whatsmyname(username):
    try:
        r = requests.get(f"https://whatsmyname.app/api/v1/username?username={username}", headers=get_headers(), timeout=15)
        if r.status_code == 200:
            data = r.json()
            sites = []
            for site in data.get('sites', []):
                if site.get('status') == "claimed" or site.get('exists'):
                    sites.append({
                        'name': site.get('site_name'),
                        'url': site.get('url'),
                        'category': site.get('category', 'social')
                    })
            return sites
        return []
    except:
        return []

# 7. API psbdmp (pastebin leaks)
def search_psbdmp(query):
    try:
        r = requests.get(f"https://psbdmp.ws/api/search/{urllib.parse.quote(query)}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'data' in data:
                return data['data'][:20]
        return []
    except:
        return []

# 8. API intelx (gratuite avec limite)
def search_intelx(query):
    try:
        r = requests.get(f"https://intelx.io/phonebook?query={urllib.parse.quote(query)}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# 9. API wigle (wifi networks - geolocalisation)
def search_wigle(ssid):
    try:
        r = requests.get(f"https://api.wigle.net/api/v2/network/search?ssid={urllib.parse.quote(ssid)}", 
                        headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# 10. API hunter (recherche emails par domaine)
def search_hunter(domain):
    try:
        r = requests.get(f"https://api.hunter.io/v2/domain-search?domain={domain}", headers=get_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

# ========== FONCTION DOXX COMPLETE AVEC 20+ BASES ==========

def doxx_super_ultime(prenom, nom):
    nom_complet = f"{prenom} {nom}"
    nom_sans_espace = f"{prenom}{nom}"
    nom_point = f"{prenom}.{nom}"
    
    # Generation emails potentiels
    domaines = ["gmail.com", "yahoo.fr", "hotmail.com", "outlook.com", "free.fr", "orange.fr", "laposte.net"]
    emails_potentiels = []
    for domaine in domaines:
        emails_potentiels.append(f"{prenom}.{nom}@{domaine}")
        emails_potentiels.append(f"{prenom}{nom}@{domaine}")
        emails_potentiels.append(f"{prenom}_{nom}@{domaine}")
        emails_potentiels.append(f"{prenom[0]}{nom}@{domaine}")
    
    # Generation usernames potentiels
    usernames_potentiels = [nom_complet.lower(), nom_sans_espace.lower(), nom_point.lower(), 
                            f"{prenom}_{nom}".lower(), f"{prenom}{nom}123", f"{nom}{prenom}".lower(),
                            prenom.lower(), nom.lower()]
    
    resultats = {
        "breaches_breachdirectory": [],
        "breaches_hibp": [],
        "breaches_leakcheck": [],
        "emails_confirmed": [],
        "numeros": [],
        "adresses": [],
        "mots_de_passe": [],
        "reseau_sociaux": [],
        "pastebin_leaks": [],
        "ips": [],
        "domaines": [],
        "entreprises": [],
        "wifi_networks": []
    }
    
    # 1. Recherche breachdirectory sur nom complet
    print("Recherche breachdirectory...")
    bd_results = search_breachdirectory(nom_complet)
    for item in bd_results[:20]:
        if isinstance(item, dict):
            if 'password' in item and item['password']:
                resultats["mots_de_passe"].append(item['password'])
            if 'email' in item and item['email']:
                resultats["emails_confirmed"].append(item['email'])
            if 'phone' in item and item['phone']:
                resultats["numeros"].append(item['phone'])
            if 'address' in item and item['address']:
                resultats["adresses"].append(item['address'])
    
    # 2. Recherche sur tous les emails potentiels
    for email in emails_potentiels[:10]:
        hibp = search_hibp(email)
        if hibp:
            resultats["breaches_hibp"].extend(hibp)
        emailrep = search_emailrep(email)
        if emailrep and emailrep.get('reputation'):
            resultats["emails_confirmed"].append(email)
    
    # 3. Recherche usernames sur reseaux sociaux
    for username in usernames_potentiels[:8]:
        socials = search_whatsmyname(username)
        for social in socials[:10]:
            resultats["reseau_sociaux"].append(f"{social['name']}: {social['url']}")
    
    # 4. Recherche pastebin leaks
    for query in [nom_complet, nom_sans_espace, prenom]:
        pastes = search_psbdmp(query)
        for paste in pastes[:5]:
            resultats["pastebin_leaks"].append(paste.get('title', '')[:100])
    
    # 5. Recherche emails supplementaires via hunter (si domaine connu)
    # 6. Nettoie et deduplique
    resultats["mots_de_passe"] = list(set(resultats["mots_de_passe"]))
    resultats["emails_confirmed"] = list(set(resultats["emails_confirmed"]))
    resultats["numeros"] = list(set(resultats["numeros"]))
    resultats["adresses"] = list(set(resultats["adresses"]))
    resultats["reseau_sociaux"] = list(set(resultats["reseau_sociaux"]))[:30]
    
    # Formatage final
    output = f"""
╔══════════════════════════════════════════════════════════════════╗
║         ⚠️  DOXX ULTIME COMPLET  ⚠️                                ║
║         {prenom.upper()} {nom.upper()}                                        
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│ 📧 EMAILS CONFIRMES ({len(resultats['emails_confirmed'])})                                         │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {e[:50]}" for e in resultats['emails_confirmed'][:15]]) if resultats['emails_confirmed'] else "│ Aucun email trouve"}

┌─────────────────────────────────────────────────────────────────┐
│ 📱 NUMEROS DE TELEPHONE ({len(resultats['numeros'])})                                           │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {n}" for n in resultats['numeros'][:10]]) if resultats['numeros'] else "│ Aucun numero trouve"}

┌─────────────────────────────────────────────────────────────────┐
│ 🏠 ADRESSES PHYSIQUES ({len(resultats['adresses'])})                                           │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {a[:60]}" for a in resultats['adresses'][:10]]) if resultats['adresses'] else "│ Aucune adresse trouvee"}

┌─────────────────────────────────────────────────────────────────┐
│ 🔓 MOTS DE PASSE EN CLAIR ({len(resultats['mots_de_passe'])})                                       │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {p[:40]}" for p in resultats['mots_de_passe'][:20]]) if resultats['mots_de_passe'] else "│ Aucun mot de passe trouve"}

┌─────────────────────────────────────────────────────────────────┐
│ 🌐 RESEAUX SOCIAUX TROUVES ({len(resultats['reseau_sociaux'])})                                  │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {s[:70]}" for s in resultats['reseau_sociaux'][:25]]) if resultats['reseau_sociaux'] else "│ Aucun compte social trouve"}

┌─────────────────────────────────────────────────────────────────┐
│ 📂 PASTEBIN LEAKS ({len(resultats['pastebin_leaks'])})                                            │
├─────────────────────────────────────────────────────────────────┤
{chr(10).join([f"│ {p[:70]}" for p in resultats['pastebin_leaks'][:10]]) if resultats['pastebin_leaks'] else "│ Aucun pastebin trouve"}

┌─────────────────────────────────────────────────────────────────┐
│ 💀 BREACHES DATABASES SCRAPEES                                   │
├─────────────────────────────────────────────────────────────────┤
│ • Breachdirectory: {len(bd_results)} entrees
│ • HIBP: {len(resultats['breaches_hibp'])} breaches
│ • Emails tests: {len(emails_potentiels)} potentiels
│ • Usernames tests: {len(usernames_potentiels)} potentiels

┌─────────────────────────────────────────────────────────────────┐
│ 🔗 LIENS SITES JEUNES & RESEAUX (A VISITER)                     │
├─────────────────────────────────────────────────────────────────┤
│ https://www.copainsdavant.com/recherche?q={urllib.parse.quote(nom_complet)}
│ https://www.trombi.com/recherche?name={nom}
│ https://www.letudiant.fr/annuaire-anciens-etudiants/recherche?q={urllib.parse.quote(prenom)}+{nom}
│ https://www.pagesjaunes.fr/pagesblanches/recherche?nom={nom}&prenom={prenom}
│ https://www.verif.com/recherche/?q={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
│ https://www.facebook.com/search/top?q={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
│ https://www.instagram.com/web/search/topsearch/?query={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
│ https://www.tiktok.com/search?q={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
│ https://twitter.com/search?q={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
│ https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(prenom)}+{urllib.parse.quote(nom)}
╚══════════════════════════════════════════════════════════════════╝
"""
    return output

# ========== AUTRES COMMANDES ILLEGALES ==========

def phone_ultra(numero):
    try:
        r = requests.get(f"http://apilayer.net/api/validate?access_key=&number={numero}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Ajout recherche breach sur numero
            breaches = search_breachdirectory(numero)
            breach_text = ""
            if breaches:
                breach_text = f"\n🔓 Leaks contenant ce numero: {len(breaches)} entrees"
            return f"""```yaml
=== TELEPHONE ULTRA ===
Numero: {data.get('number')}
International: {data.get('international_format')}
Pays: {data.get('country_name')}
Operateur: {data.get('carrier')}
Ligne: {data.get('line_type')}
Valide: {data.get('valid')}
{breach_text}
```"""
        return "Numero invalide"
    except:
        return "Erreur telephone"

def email_ultra(email):
    try:
        emailrep = search_emailrep(email)
        hibp = search_hibp(email)
        breaches = search_breachdirectory(email)
        return f"""```yaml
=== EMAIL ULTRA ===
Email: {email}
Reputation: {emailrep.get('reputation', 'inconnue')}
Suspect: {emailrep.get('suspicious', 'non')}
Breaches HIBP: {len(hibp)} sites
Leaks breachdirectory: {len(breaches)} entrees
Mots de passe trouves: {[b['password'] for b in breaches if 'password' in b][:5]}
```"""
    except:
        return "Erreur email"

def ip_ultra(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,mobile,proxy,hosting,query", timeout=5)
        data = r.json()
        # Recherche de l'IP dans les breaches
        breach_ip = search_psbdmp(ip)
        return f"""```yaml
=== IP ULTRA ===
IP: {data.get('query')}
Pays: {data.get('country')}
Region: {data.get('regionName')}
Ville: {data.get('city')}
Lat/Lon: {data.get('lat')}/{data.get('lon')}
FAI: {data.get('isp')}
Proxy/VPN: {data.get('proxy')}
Datacenter: {data.get('hosting')}
Pastebins contenant cette IP: {len(breach_ip)}
```"""
    except:
        return "Erreur IP"

def username_ultra(username):
    try:
        socials = search_whatsmyname(username)
        breaches = search_breachdirectory(username)
        return f"""```yaml
=== USERNAME ULTRA ===
Username: {username}
Comptes trouves: {len(socials)}
{chr(10).join([f'- {s["name"]}: {s["url"]}' for s in socials[:20]])}
Leaks contenant ce username: {len(breaches)}
Mots de passe: {[b['password'] for b in breaches if 'password' in b][:5]}
```"""
    except:
        return "Erreur username"

def social_ultra(platform, username):
    platforms_urls = {
        "instagram": f"https://www.instagram.com/{username}/",
        "twitter": f"https://twitter.com/{username}",
        "facebook": f"https://facebook.com/{username}",
        "tiktok": f"https://tiktok.com/@{username}",
        "snapchat": f"https://snapchat.com/add/{username}",
        "reddit": f"https://reddit.com/user/{username}",
        "github": f"https://github.com/{username}",
        "linkedin": f"https://linkedin.com/in/{username}",
        "youtube": f"https://youtube.com/@{username}",
        "pinterest": f"https://pinterest.com/{username}/"
    }
    if platform not in platforms_urls:
        return "Platformes: instagram, twitter, facebook, tiktok, snapchat, reddit, github, linkedin, youtube, pinterest"
    try:
        r = requests.get(platforms_urls[platform], headers=get_headers(), timeout=10)
        existe = r.status_code == 200
        # Recherche de l'username dans breaches
        breaches = search_breachdirectory(username)
        return f"""```yaml
=== {platform.upper()} ===
Username: {username}
URL: {platforms_urls[platform]}
Compte existe: {existe}
Leaks contenant cet username: {len(breaches)}
Infos supplementaires: {[b for b in breaches[:3] if 'password' in b]}
```"""
    except:
        return f"Erreur verification {platform}"

def domain_ultra(domain):
    try:
        r = requests.get(f"https://api.hackertarget.com/whois/?q={domain}", timeout=15)
        whois_data = r.text[:1500] if r.status_code == 200 else "WHOIS indisponible"
        emails_domain = search_hunter(domain)
        return f"""```yaml
=== DOMAIN ULTRA ===
Domaine: {domain}
WHOIS: 
{whois_data}
Emails associes au domaine:
{chr(10).join([e['value'] for e in emails_domain.get('data', {}).get('emails', [])[:10]]) if emails_domain else 'Aucun email trouve'}
```"""
    except:
        return "Erreur domaine"

def breach_ultra(query):
    try:
        bd = search_breachdirectory(query)
        psbdmp = search_psbdmp(query)
        return f"""```yaml
=== RECHERCHE BREACH ULTRA ===
Requete: {query}
Breachdirectory: {len(bd)} entrees
Pastebin/Psbdmp: {len(psbdmp)} resultats

PREMIERES ENTREES BREACHDIRECTORY:
{json.dumps(bd[:5], indent=2)[:1500] if bd else 'Aucune'}

PASTEBIN LEADS:
{chr(10).join([p.get('title', '')[:100] for p in psbdmp[:5]]) if psbdmp else 'Aucun'}
```"""
    except:
        return "Erreur recherche breach"

# ========== COMMANDES SLASH ==========

@tree.command(name="doxx", description="TOUT sur une personne - nom, prenom donne TOUTES infos personnelles, mots de passe, adresses, leaks")
@app_commands.describe(prenom="Prenom de la cible", nom="Nom de famille")
async def doxx(interaction: discord.Interaction, prenom: str, nom: str):
    await interaction.response.defer()
    result = doxx_super_ultime(prenom, nom)
    embed = discord.Embed(title=f"⚠️ DOXX ULTIME - {prenom.upper()} {nom.upper()}", description=result[:4000], color=0xff0000)
    await interaction.followup.send(embed=embed)

@tree.command(name="phone", description="Recherche telephone - operateur, localisation, leaks")
@app_commands.describe(numero="Numero de telephone (format international)")
async def phone_slash(interaction: discord.Interaction, numero: str):
    await interaction.response.defer()
    await interaction.followup.send(phone_ultra(numero))

@tree.command(name="email", description="Recherche email - reputation, breaches, mots de passe")
@app_commands.describe(email="Adresse email")
async def email_slash(interaction: discord.Interaction, email: str):
    await interaction.response.defer()
    await interaction.followup.send(email_ultra(email))

@tree.command(name="ip", description="Recherche IP - geoloc, FAI, proxy, pastebins")
@app_commands.describe(ip="Adresse IP")
async def ip_slash(interaction: discord.Interaction, ip: str):
    await interaction.response.defer()
    await interaction.followup.send(ip_ultra(ip))

@tree.command(name="username", description="Recherche username sur 400+ sites + leaks")
@app_commands.describe(username="Nom d'utilisateur")
async def username_slash(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    await interaction.followup.send(username_ultra(username))

@tree.command(name="social", description="Verifie existence compte sur reseau social + leaks")
@app_commands.describe(platform="instagram, twitter, facebook, tiktok, snapchat, reddit, github, linkedin", username="Nom d'utilisateur")
async def social_slash(interaction: discord.Interaction, platform: str, username: str):
    await interaction.response.defer()
    await interaction.followup.send(social_ultra(platform, username))

@tree.command(name="domain", description="WHOIS + emails associes au domaine")
@app_commands.describe(domain="Nom de domaine (ex: google.com)")
async def domain_slash(interaction: discord.Interaction, domain: str):
    await interaction.response.defer()
    await interaction.followup.send(domain_ultra(domain))

@tree.command(name="breach", description="Recherche dans toutes les breaches + pastebin")
@app_commands.describe(query="Email, username, telephone ou nom a rechercher")
async def breach_slash(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    await interaction.followup.send(breach_ultra(query))

@tree.command(name="jeunes", description="Liens directs vers sites jeunes et reseaux sociaux")
@app_commands.describe(prenom="Prenom", nom="Nom")
async def jeunes_slash(interaction: discord.Interaction, prenom: str, nom: str):
    await interaction.response.defer()
    result = doxx_super_ultime(prenom, nom)
    # Extrait juste la partie sites jeunes
    lignes = result.split('\n')
    jeunes_partie = []
    capture = False
    for ligne in lignes:
        if "LIENS SITES JEUNES" in ligne:
            capture = True
        if capture:
            jeunes_partie.append(ligne)
        if capture and "╚════" in ligne:
            break
    await interaction.followup.send(f"```\n{chr(10).join(jeunes_partie[:40])}\n```")

# ========== COMMANDES PREFIX ==========
@bot.command(name="doxx")
async def cmd_doxx(ctx, prenom: str, nom: str):
    await ctx.send(doxx_super_ultime(prenom, nom))

@bot.command(name="phone")
async def cmd_phone(ctx, numero: str):
    await ctx.send(phone_ultra(numero))

@bot.command(name="email")
async def cmd_email(ctx, email: str):
    await ctx.send(email_ultra(email))

@bot.command(name="ip")
async def cmd_ip(ctx, ip: str):
    await ctx.send(ip_ultra(ip))

@bot.command(name="username")
async def cmd_username(ctx, username: str):
    await ctx.send(username_ultra(username))

@bot.command(name="social")
async def cmd_social(ctx, platform: str, username: str):
    await ctx.send(social_ultra(platform, username))

@bot.command(name="domain")
async def cmd_domain(ctx, domain: str):
    await ctx.send(domain_ultra(domain))

@bot.command(name="breach")
async def cmd_breach(ctx, *, query: str):
    await ctx.send(breach_ultra(query))

@bot.command(name="jeunes")
async def cmd_jeunes(ctx, prenom: str, nom: str):
    result = doxx_super_ultime(prenom, nom)
    lignes = result.split('\n')
    jeunes_partie = []
    capture = False
    for ligne in lignes:
        if "LIENS SITES JEUNES" in ligne:
            capture = True
        if capture:
            jeunes_partie.append(ligne)
        if capture and "╚════" in ligne:
            break
    await ctx.send(f"```\n{chr(10).join(jeunes_partie[:40])}\n```")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ BOT DOXX ULTIME ACTIF - 9 commandes slash + 9 commandes prefix")
    print("Commandes: /doxx, /phone, /email, /ip, /username, /social, /domain, /breach, /jeunes")
    print("Prefix: !doxx, !phone, !email, !ip, !username, !social, !domain, !breach, !jeunes")

if __name__ == "__main__":
    bot.run(TOKEN)