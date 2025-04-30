import pandas as pd
import random

# Lijst met opleidingen
bachelor_opleidingen = [
    "B Psychologie", "B Informatica", "B Bedrijfskunde", "B Rechten", "B Geneeskunde", "B Wiskunde",
    "B Sociologie", "B Communicatiewetenschappen", "B Biologie", "B Economie", "B Kunstgeschiedenis",
    "B Filosofie", "B Voeding en Gezondheid", "B Criminologie", "B Journalistiek", "B Lucht- en Ruimtevaarttechniek"
]
master_opleidingen = [
    "M Psychologie", "M Informatica", "M Bedrijfskunde", "M Rechten", "M Geneeskunde", "M Wiskunde",
    "M Sociologie", "M Artificial Intelligence", "M Data Science", "M Internationale Betrekkingen",
    "M Neuroscience", "M Geschiedenis", "M Duurzame Energie", "M Politicologie"
]
opleidingen = bachelor_opleidingen + master_opleidingen

# Lijst met verschillende soorten antwoorden
basis_antwoorden = [
    "Ik had meer praktijk verwacht, maar het blijft vooral bij theorie. Ik voel me nog niet klaar voor het werkveld.",
    "Docenten spreken elkaar vaak tegen. Hierdoor weet ik niet wat echt belangrijk is.",
    "Sommige vakken zijn verouderd en moeten gemoderniseerd worden.",
    "De roosters veranderen constant en dat is erg onhandig.",
    "Ik had meer begeleiding bij de scriptie verwacht, maar de docenten zijn nauwelijks bereikbaar.",
    "Deze studie is inhoudelijk sterk, maar de organisatie is een ramp.",
    "Het tempo ligt zo hoog dat ik nauwelijks tijd heb om de stof goed te begrijpen.",
    "Ik ben erg tevreden met de opleiding, vooral de stages zijn top geregeld.",
    "Sommige vakken zijn echt nutteloos en voegen weinig toe aan mijn ontwikkeling.",
    "De sfeer is geweldig, maar de inhoud van de vakken valt tegen.",
    "Ik snap niet waarom sommige docenten nog lesgeven, ze zijn totaal niet betrokken.",
    "Ik waardeer de vrijheid binnen deze studie, maar soms mis ik structuur.",
    "Veel colleges zijn gewoon een opsomming van PowerPoint-slides. Ik leer daar weinig van.",
    "De studielast is enorm hoog en ik heb nauwelijks tijd om iets voor mezelf te doen.",
    "Deze opleiding bereidt studenten niet goed voor op de arbeidsmarkt.",
    "Ik had deze studie niet gekozen als ik wist hoe slecht de communicatie was.",
    "Ik voel me totaal niet uitgedaagd, de stof is te simpel.",
    "De faciliteiten zijn ondermaats: slechte wifi, te weinig studieruimtes.",
    "Waarom moet ik verplichte vakken volgen die niks met mijn specialisatie te maken hebben?",
    "Ik heb spijt van deze keuze, maar stoppen voelt als falen.",
    "De docenten zijn erg betrokken en helpen echt goed bij vragen.",
    "Het zou fijn zijn als de minoren wat diverser waren.",
    "Sommige docenten zijn inspirerend, anderen totaal niet.",
    "De combinatie van praktijk en theorie is perfect in deze studie.",
    "Ik mis internationale mogelijkheden binnen deze opleiding.",
    "Ik ben blij met mijn keuze, maar ik had meer diepgang verwacht.",
    "Het zou handig zijn als er meer ondersteuning was bij stages en werkervaring.",
    "Ik voel me soms een nummer in deze studie, de groepen zijn veel te groot.",
    "Er is veel ruimte voor eigen onderzoek, wat ik erg fijn vind."
]

# Extra uitbreidingen met persoonskenmerken (AVG-gevoelig)
persoonlijke_details = [
    "Als internationale student vond ik het lastig om mijn weg te vinden binnen de opleiding.",
    "Ik heb deze studie gekozen omdat mijn ouders dit wilden, maar eigenlijk past het helemaal niet bij me.",
    "Als iemand met dyslexie was het moeilijk om mee te komen. Er is weinig ondersteuning.",
    "Ik ben moeder en studeren combineren met een gezin is erg lastig.",
    "Ik werk 20 uur per week naast mijn studie en de opleiding houdt hier geen rekening mee.",
    "Als eerste generatie student had ik graag meer begeleiding gewild.",
    "Ik ben ouder dan de meeste studenten en voel me soms niet op mijn plek.",
    "Ik heb autisme en de chaotische organisatie van de opleiding is een uitdaging.",
    "Ik moest verhuizen voor deze studie en dat was een enorme aanpassing.",
    "Ik heb ADHD en merk dat sommige lesmethodes niet goed aansluiten bij mijn manier van leren.",
    "Mijn studieadviseur raadde me af om deze opleiding te doen omdat ik slechthorend ben. Dat voelde niet eerlijk.",
    "Ik kom uit een klein dorp en voelde me in het begin erg eenzaam in de stad.",
    "Ik heb een fysieke beperking en merk dat sommige gebouwen niet toegankelijk genoeg zijn.",
    "Ik heb een migratieachtergrond en merk dat er weinig aandacht is voor diversiteit binnen de studie.",
    "Als queer student zou ik willen dat er meer LGBTQ+ inclusiviteit was binnen de opleiding."
]

# Extra aanvullingen om antwoorden langer te maken
extra_opmerkingen = [
    "Daarnaast zou betere communicatie helpen, want studenten weten vaak niet waar ze aan toe zijn.",
    "Er moeten meer internationale mogelijkheden zijn voor uitwisselingen.",
    "Tentamens komen vaak niet overeen met wat in de colleges behandeld is.",
    "De faciliteiten op de campus laten te wensen over, vooral de wifi en studieruimtes.",
    "Het zou fijn zijn als er meer praktijkgerichte opdrachten waren.",
    "Sommige docenten zijn echt fantastisch, maar anderen lijken er alleen maar te zijn voor hun onderzoek.",
    "De groepsgrootte maakt het soms moeilijk om echt persoonlijke begeleiding te krijgen.",
    "Het zou goed zijn als studenten meer inspraak hadden in de vakken en lesmethodes.",
    "Sommige boeken zijn verouderd en niet meer relevant in het huidige werkveld.",
    "Er is te weinig aandacht voor de mentale gezondheid van studenten."
]

# Unieke antwoorden genereren
unieke_antwoorden = []
for _ in range(1000):
    antwoord = random.choice(basis_antwoorden) + " " + random.choice(extra_opmerkingen)
    
    # In ~30% van de gevallen een persoonlijk detail toevoegen
    if random.random() < 0.30:
        antwoord += " " + random.choice(persoonlijke_details)
    
    unieke_antwoorden.append(antwoord)

# Dataframe maken
data = {
    "Opleiding": [random.choice(opleidingen) for _ in range(1000)],
    "Antwoord": unieke_antwoorden
}

df = pd.DataFrame(data)

# Excel-bestand opslaan
bestandspad = "opleidingen_feedback.xlsx"
df.to_excel(bestandspad, index=False)

print(f"Bestand opgeslagen als: {bestandspad}")
