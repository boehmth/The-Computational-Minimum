# Vorwort

## Warum dieses Buch, warum jetzt?

Jede Generation hat eine Technologie, deren Grundprinzipien man verstehen sollte, um in ihrer Zeit mündig zu bleiben.

- Um **1920** war das das **Automobil** — vom Luxusgut der Wohlhabenden zum Alltagsgegenstand. Wer damals nicht mit Motor und Verbrennung, mit Straßen und Verkehrsordnung umzugehen lernte, blieb zurück.
- Um **1960** waren es **Fernseher und Telefon in jedem Haushalt** — die erste elektronische Alltagswelt, die Kommunikation und Information neu definierte.
- Um **1990** war es der **Computer** — vom Werkzeug der Enthusiasten und Rechenzentren zum Werkzeug jedes Berufstätigen. Wer 1985 sagte *„ich brauche keinen Computer"*, stand 2005 vor einer Wand.
- Um **2010** wurde das **Internet** endgültig zur Grundlage aller Kommunikation, allen Wissens, aller Arbeit.

Und jetzt, in den **2020er-Jahren**, kommt die **Künstliche Intelligenz** — die nächste dieser Technologien, die von der Nische in den Alltag rutscht.

**Der Unterschied zu allen vorhergehenden Wellen:** KI wird nicht nur ein neues Werkzeug sein, sondern ein **System, das Antworten gibt, Entscheidungen begründet, Texte schreibt, Bilder erzeugt, argumentiert**. Ein System, das aussieht, als würde es *verstehen*. Und genau deshalb reicht es nicht, sie nur bedienen zu können. Man muss sie **mündig hinterfragen** können:

- Wie kommen ihre Antworten zustande?
- Was kann das Modell wirklich, was scheint es nur zu können?
- Wo sind die harten Grenzen?
- Wann sollte ich ihm glauben, wann nicht?

Dieses Buch versucht, seiner Leserschaft — Abiturient:innen, Studienanfänger:innen, technisch neugierige Erwachsene — **das Fundament** zu geben, das für diese Mündigkeit nötig ist. Nicht der Umgang mit ChatGPT. Sondern das **Verständnis davon, was ChatGPT tut** und woher es kommt.

In acht selbst programmierten Meilensteinen. Ohne Frameworks. Ohne verstecktes Wissen.

---

## In der Tradition des „Theoretical Minimum"

Der Titel dieser Reihe lehnt sich bewusst an **Leonard Susskinds „Theoretical Minimum"** an — jene wunderbare Buchreihe, in der ein weltweit anerkannter Physiker versucht, die *echte* moderne Physik in ihrer minimalen, aber vollständigen Form aufzuschreiben. Susskind schreibt nicht für Fachleute, aber auch nicht populärwissenschaftlich weichgespült. Er schreibt für Erwachsene, die die Sache **verstehen** wollen und dafür bereit sind, Formeln zu lesen und einen Bleistift in die Hand zu nehmen.

Eine zweite Inspiration ist **Sean Carrolls „Biggest Ideas in the Universe"** — die Idee, physikalische Kernkonzepte einer breiten, interessierten Öffentlichkeit so aufzubereiten, dass sie *tatsächlich* zugänglich werden, ohne dass die Substanz verloren geht. Auch hier: Nicht *„vereinfacht"*, sondern *„auf das Wesentliche reduziert"*.

Was Physik in Susskinds und Carrolls Werken ist, soll die **Künstliche Intelligenz** in dieser Reihe sein: ein Feld, das viele Menschen betrifft, aber nur wenige wirklich verstehen — und das genau deshalb aufgeschlüsselt gehört. Der gesellschaftliche Einfluss der KI wird die nächsten Jahrzehnte prägen. Umso wichtiger ist es, dass es Menschen gibt, die sie *im Kern* verstehen — nicht nur die Marketing-Version.

---

## Was diese Reihe anders macht

Der Markt hat viele KI-Bücher, aber die meisten fallen in eine dieser drei Kategorien:

1. **Framework-Kochbücher** (*„So baust du ein RNN mit PyTorch"*): zeigen *wie*, nicht *warum*. Der Leser lernt eine API, nicht das Feld.
2. **Wissenschaftliche Lehrbücher** (Goodfellow, Bishop): tief, präzise, mathematisch — aber 800+ Seiten und ohne narrativen Faden.
3. **Populärwissenschaft** (*„KI für Neugierige"*): angenehm zu lesen, aber ohne Code, ohne Details, ohne echte Substanz.

Dieses Buch geht einen **vierten Weg**:

- **Kompakt.** Acht Meilensteine, jeder in wenigen Stunden durcharbeitbar.
- **Mit lauffähigem Code.** Jedes Modell in reinem Python bzw. NumPy — kein Framework versteckt das Wesentliche.
- **Historisch erzählt.** Wer, wann, wo, warum — jeder Meilenstein hat Gesichter, Jahre, Papers.
- **Ehrlich eingeordnet.** Was ist heute noch aktuell? Was ist nur Vorgeschichte? Die Reihe belügt den Leser nicht darüber, dass ein Vanilla-RNN 2025 nicht mehr die state-of-the-art Wahl ist.

**Was der Leser am Ende hat:** nicht nur die Fähigkeit, GPT zu erklären, sondern die Fähigkeit, **jede zukünftige KI-Neuheit einzuordnen**. Denn er hat die Bausteine selbst gebaut. Er weiß, welche Grenzen die Bausteine haben, warum sie kombiniert werden, und was der eigentliche Fortschritt der letzten Jahre wirklich ist.

---

## Struktur der Reihe

Diese Reihe ist Teil eines **dreiteiligen Projekts**:

- **[01_Computing](01_Computing/)** — *Milestones in Computing:* Wie funktioniert ein Computer überhaupt? Rechnerarchitektur, Betriebssystem, Compiler, Netzwerke — die zeitlosen Grundlagen der Informatik, jeweils als selbst gebautes Miniaturmodell.
- **[02_MachineIntelligence](02_MachineIntelligence/)** — *Milestones in Machine Intelligence:* Sechzig Jahre neuronale Netze in acht Meilensteinen. Vom Perceptron (1958) über CNN, Word2Vec, RNN, Seq2Seq, Attention und Transformer bis zum eigenen kleinen GPT (2018). Alles selbst programmiert, alles nachvollziehbar. Der Begriff *„Machine Intelligence"* stammt aus Turings ursprünglichem Aufsatz von 1950 und vermeidet den Marketing-Ton von „AI".
- **[03_AgenticSystems](03_AgenticSystems/)** *(in Vorbereitung)* — *Milestones in Agentic Systems:* Was in den letzten zehn Jahren aus diesen Grundlagen konkret gebaut wurde. LLMs im Detail, Mixture-of-Experts, Domänen-Transformer (Zeitreihen, Tabellen, Proteine), Reasoning-Modelle (DeepSeek-R1, o1), Multimodalität, Werkzeug-Nutzung, autonome Agenten. Der Übergang von *„Text produzieren"* zu *„Aufgaben erledigen"*.

Am Ende dieser drei Teile hat der Leser **von Bit und Byte bis zum autonomen KI-Agenten** einen durchgängigen Bogen. Kein Zauber. Nur Handwerk. Und ein sechzig­jähriger Wissenschaftspfad, den man Schritt für Schritt gehen kann.

---

## An wen richtet sich dieses Buch?

**Zuerst an Jugendliche und junge Erwachsene**, die technisch neugierig sind und Python auf Grundstufen­niveau beherrschen. Wer das Perceptron-Kapitel bis zum Ende versteht, kann alle folgenden Kapitel bewältigen.

**Zweitens an Lehrkräfte** in Oberstufen, an Universitäten oder in KI-Weiter­bildungen, die einen roten Faden für Kurse suchen — nicht ein weiteres PyTorch-Notebook, sondern einen didaktischen Aufbau, der die *Motivation* jeder Technik zeigt.

**Drittens an Informatikerinnen und Informatiker anderer Fachrichtungen** (Softwareentwicklung, Datenbanken, Systeme, Security …), die den KI-Bereich systematisch aufholen möchten. Wer diese Reihe durchgearbeitet hat, kann jedes moderne KI-Paper lesen — nicht mit dem Anspruch, jede Formel im Detail zu beherrschen, aber mit der Fähigkeit, den Beitrag der Arbeit **einzuordnen**.

---

## Ein persönliches Wort

Diese Reihe entsteht aus einer sehr persönlichen Beobachtung: **Meine eigene Tochter wird in einer Welt aufwachsen, in der KI omnipräsent ist.** Sie wird sie so selbstverständlich benutzen, wie meine Generation den PC benutzt und die vorherige das Telefon. Der Unterschied: KI ist die erste Technologie in dieser Reihe, die *aussieht*, als würde sie *denken*. Und genau deshalb braucht die nächste Generation nicht nur Benutzer­kompetenz, sondern **Deutungs­kompetenz**.

Wenn dieses Buch dazu beiträgt, dass ein paar dieser jungen Menschen KI nicht mit Ehrfurcht und nicht mit Angst begegnen, sondern mit **wachem Verständnis** — dann hat es seine Aufgabe erfüllt.

Viel Freude beim Durcharbeiten.

*[Dein Name]*