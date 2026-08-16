# Projet TFC LaTeX — version mise à jour

Cette version respecte la structure des chapitres et des points du document Word source.

## Structure
- Chapitre I : Revue de la littérature et fondements théoriques
- Chapitre II : Cadre méthodologique et présentation du milieu d'étude
- Chapitre III : Conception et développement d'un jumeau numérique intégrant l'intelligence artificielle

Les chapitres commencent sur une nouvelle page et les niveaux de titres suivent la numérotation du document source : 1.1, 1.1.1, 2.1, 2.2.1, 3.1, 3.2.1, etc.

## Important
Le document Word annonce quatre chapitres dans la section « Subdivision du mémoire », mais le contenu fourni s'arrête au Chapitre III puis passe à la bibliographie. Aucun contenu de Chapitre IV n'a donc été inventé.

## Compilation
Utiliser :
1. pdflatex main.tex
2. biber main
3. pdflatex main.tex
4. pdflatex main.tex

Le projet utilise BibLaTeX avec le style IEEE.
