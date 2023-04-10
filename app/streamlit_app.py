import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import urllib.request
import zipfile
import io 
import itertools
import operator as op
import requests
# ---------------------------------------------------------------------
# Config streamlit
#-----------------------------------------------------------------------------------
st.set_page_config(page_title="Proto LOTO", page_icon=":tada:", layout="wide")


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#                        CHARGEMENT DES DONNEES
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Recuperation du fichier sur le site du loto
url = "https://media.fdj.fr/static-draws/csv/loto/loto_201911.zip" # URL du fichier zip à télécharger

response = requests.get(url)
zip_file = zipfile.ZipFile(io.BytesIO(response.content))

# Décompression du fichier ZIP
zip_file.extractall()
zip_file.close()

# Lecture du fichier CSV
with open(zip_file.namelist()[0], 'r') as file:
    data = pd.read_csv(file, sep=";")

# Nettoyage du Dataset pour avoir uniquement des nombres et pas des strings
for i in range(2,8):
    data[f"rapport_du_rang{i}"] = data[f"rapport_du_rang{i}"].apply(lambda x: float(x.replace(",", ".")))
for i in range(2,4):
    data[f"rapport_du_rang{i}_second_tirage"] = data[f"rapport_du_rang{i}_second_tirage"].apply(lambda x: float(x.replace(",", ".")))

data['combinaison_gagnante_en_ordre_croissant'] = data['combinaison_gagnante_en_ordre_croissant'].apply(lambda x: x.split("+")[0])
data['combinaison_gagnante_en_ordre_croissant'] = data['combinaison_gagnante_en_ordre_croissant'].apply(lambda x: x.split("-"))


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   DEFINITION DES FONCTION POUR LA REDUCTION DE COMBINAISONS
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Comparer les numéros voulus par l'utilisateur à ceux présent dans le tirage
def numeros_voulus(tirage,liste_numeros_voulus):
    if liste_numeros_voulus[0]==0:
        if liste_numeros_voulus[1]==0:
            return True
        else:
            if liste_numeros_voulus[1] in tirage:
                return True
            else:
                return False
    else:
        if liste_numeros_voulus[0] in tirage:
            if liste_numeros_voulus[1]==0:
                return True
            elif liste_numeros_voulus[1] in tirage:
                return True
            else:
                return False
        else:
            return False
        

# Comparer les numéros non voulus par l'utilisateur à ceux présent dans le tirage
def numeros_non_voulus(tirage,liste_numeros_non_voulus):
    count=0
    for i in liste_numeros_non_voulus:
        if i in tirage:
            count+=1
        else:
            pass
    if count==0:
        return True
    else:
        return False
    
# Retirer les tirages qui ont 3 chiffres consécutifs
def numeros_consecutifs_3(tirage,option):
    if option==True:
        count=0        
        for j in range(3):
            if (int(tirage[j])+1==int(tirage[j+1])) and (int(tirage[j+1])+1==int(tirage[j+2])): # si 3 numero consecutifs differetns alors on continue la selection
                count+=1
            else:
                pass
        if count==0:
            return True
        else:
            return False
    else:
        return True
    
# Retirer les tirages qui ont 2 chiffres consecutifs
def numeros_consecutifs_2(tirage,option):
    count=0
    for i in range(4):
        if tirage[i]+1==tirage[i+1] and tirage[i+1]+1==tirage[i+2]:
            return False
        else: 
            return True
    

# Choix du nombre de dizaine repésentées dans le tirage
def nb_dizaine(tirage,dizaine):
    result=[0,0,0,0,0]      
    for j in tirage:
        if j<10:
            result[0]+=1
        elif j>=10 and j<20:      #
            result[1]+=1                    #
        elif j>=20 and j<30:      #   On va classer chaque chiffre d'un tirage dans une dizaine
            result[2]+=1                    #
        elif j>=30 and j<40:      #
            result[3]+=1
        else:
            result[4]+=1
    diz = op.countOf(result, 0)        #   On regarde le nombre de dizaine à 0          
    diz_min, diz_max=dizaine[0], dizaine[1]
    if diz>=diz_min and diz<=diz_max:
        return True
    else:
        return False

def nb_paire(tirage,liste_parite):
    parite=[0,0,0,0,0]      
    for j in range(5):                   
        parite[j] = tirage[j]%2
    somme_impaire = sum(parite)
    if somme_impaire>=liste_parite[0] and somme_impaire<=liste_parite[1]:
        return True
    else:
        return False
    
def def_somme(tirage, liste_somme):
    somme_tirage=sum(tirage)
    if somme_tirage>=liste_somme[0] and somme_tirage<=liste_somme[1]:     # si la somme des chiffres du tirage est compris dans la fourchette alors on continue
        return True
    else:
        return False




#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   AFFICHAGE DES GRAPHS PERMETTANT DE FAIRE SES CHOIX
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Fréquence de sortie
st.header("Les fréquences de sorties")
table=[]
for i in range(1,50):
    table.append([i,data.iloc[:,4:9].eq(i).sum().sum()])

df = pd.DataFrame(table,columns=["nombre","freq"])
fig = plt.figure(figsize=(20,8))
sns.barplot(data=df, x=df.nombre, y=df.freq)
st.pyplot(fig)

nombre_1 = [i for i in range(1,50)]
nombre_1 = st.selectbox('Sélectionnez un nombre', nombre_1)
  

# Nombre de tirage depuis qu'un numèro n'est pas sortie
st.header("Nombre de Tirages depuis qu'un numéro n'est pas sortie")
x, y =[],[]
for i in range(1,50):
    for j in data.index:
        if i in list(map(int,data['combinaison_gagnante_en_ordre_croissant'][j])):
            x.append(i)
            y.append(j)
            break


fig = plt.figure(figsize=(20,10))
sns.barplot(x=x,y=y)
plt.title("Nombre de tirages depuis lequel un numéro n'est pas sorti")
plt.xlabel("Numéro de la boule", style='italic')
plt.ylabel("Nombre de tirages", style='italic')
st.pyplot(fig)

nombre_2 = [i for i in range(2,50)]
nombre_2 = st.selectbox('Sélectionnez un nombre (0 pour ne pas faire de choix)', nombre_2)

nombre_3 = [i for i in range(0,50)]
nombre_3 = st.selectbox('Sélectionnez un nombre que vous voulez exclure (0 pour ne pas faire de choix)', nombre_3)
nombre_4 = [i for i in range(0,50)]
nombre_4 = st.selectbox('Sélectionnez un nombre que vous voulez exclure(0 pour ne pas faire de choix)', nombre_4)

# Retards et fréquence de sortie sur le numéro chance
st.header("Retards et fréquence de sortie sur le numéro chance")
x, y =[],[]
for i in range(1,11):
    for j in data.index:
        if i==data['numero_chance'][j]:
            x.append(i)
            y.append(j)
            break

table=[]
for i in range(1,11):
    table.append([i,data.loc[:,"numero_chance"].eq(i).sum().sum()])
df = pd.DataFrame(table,columns=["nombre","freq"])

fig,ax=plt.subplots(1,2,figsize=(20,8))
sns.barplot(x=x,y=y,ax=ax[0])
ax[0].set_title("Nombre de tirages depuis lequel un numéro n'est pas sorti")
ax[0].set_xlabel("Numéro de la boule", style='italic')
ax[0].set_ylabel("Nombre de tirages", style='italic')
sns.barplot(data=df, x=df.nombre, y=df.freq,ax=ax[1])
ax[1].set_title("Nombre de sortie")
ax[1].set_xlabel("Numéro de la boule", style='italic')
ax[1].set_ylabel("Nombre de tirages", style='italic')
st.pyplot(fig)

range_chance = [i for i in range(1,11)]
boule_chance = st.selectbox('Selectionnez un nombre', range_chance)

# Suite sur le tirage
st.header("Nombre de numéro qui se suivent dans un tirage(exempe:32 et 33 vaudra 1.0)")
for i in range(data.shape[0]):
    tirage = data.iloc[i,10]
    count=int(0)
    for j in range(4):
        if int(tirage[j])+1==int(tirage[j+1]):
            count+=1
    data.loc[data.index[i],"suite"] = count


fig = plt.figure(figsize=(20,8))
sns.countplot(x=data["suite"])
st.pyplot(fig)

suite_2 = st.radio("Voulez-vous supprimer les tirages avec deux chiffres qui se suivent ?", ("OUI", "NON"))
suite_3 = st.radio("Voulez-vous supprimer les tirages avec trois chiffres qui se suivent ?", ("OUI", "NON"))
if suite_2 == "OUI":
    suite_2 = True
else:
    suite_2 = False
if suite_3 == "OUI":
    suite_3 = True
else:
    suite_3 = False

# Repartition par dizaines : nombre de dizaine manquante sur un tirage
st.header("Nombre de dizaines manquantes sur un tirage")
for i in range(data.shape[0]): 
    result=[0,0,0,0,0]
    for j in data.iloc[i,10]:
        if int(j)<10:
            result[0]+=1
        elif int(j)>=10 and int(j)<20:
            result[1]+=1
        elif int(j)>=20 and int(j)<30:
            result[2]+=1
        elif int(j)>=30 and int(j)<40:
            result[3]+=1
        else:
            result[4]+=1
    data.loc[data.index[i],"diz_not_use"]=op.countOf(result, 0)

fig = plt.figure(figsize=(20,8))
sns.countplot(x=data["diz_not_use"])
st.pyplot(fig)

dizaine=st.slider('Nombre de dizaines manquantes :',min_value=0,max_value=5,value=(1,2))

# La parité
st.header("Répartition des numéros paires impaires sur un tirage")
for i in range(data.shape[0]):  
    tirage = data.iloc[i,10]
    somme_tirage=[0,0,0,0,0]
    for j in range(5):
        somme_tirage[j] = int(tirage[j])%2
    somme_impaire = sum(somme_tirage)
    data.loc[data.index[i],"nb_impaire"]=somme_impaire

fig = plt.figure(figsize=(20,8))
sns.countplot(x=data["nb_impaire"])
st.pyplot(fig)

parite = st.slider('Sélectionnez une valeur', min_value=0, max_value=5, value=(0,5))

# Répartition de la somme de chaque tirage
st.header("Répartition de la somme de chaque tirage")
for i in range(data.shape[0]):
    liste_str=data.iloc[i,10]
    liste_int = []
    for element in liste_str:
        liste_int.append(int(element))
        data.loc[data.index[i],"somme_tirage"]=sum(liste_int)

fig = plt.figure(figsize=(20,8))
st.write(f"Actuellement la moyenne sur un tirage est de {round(data.somme_tirage.mean(),2)} au lieu de 125")
st.write("Répartition de la somme de chaque tirage")
sns.boxplot(x=data.somme_tirage)
st.pyplot(fig)

somme=st.slider('somme du tirage MIN',min_value=15,max_value=235,value=(105,145))


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   ALGO PERMETTANT DE REDUIRE LE NOMBRE DE COMBINAISON
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


# Variables à mettre dans la sidebar
#
# option_suivi_3 = True # Si la combinaison contient 3 numéros qui se suivent la combinaison ne sera pas retenue
# option_suivi_2 = True
# parite=[2,3]
# count =0
# jeux_df = pd.DataFrame(columns=['N1','N2','N3','N4','N5','NChance'])
# boule_chance=10

numeros = list(range(1, 50))
combinaison = itertools.combinations(numeros, 5)
jeux_df = pd.DataFrame()


for combi in combinaison:
    tirage = list(combi)
    if numeros_voulus(tirage,[nombre_1,nombre_2]): # SI un numéros voulus par l'utilisateur est présent dans le tirage on continu 
        if numeros_non_voulus(tirage,[nombre_3,nombre_4]): # SI un numéro non voulu par l'utilisateur est présent on retire le tirage
            if numeros_consecutifs_3(tirage,suite_2): # S'il y a 3 chiffres consécutif on supprime le tirage
                if nb_dizaine(tirage,dizaine): # On ne garde que les tirages avec le nombre de dizaines voulus par l'utilisateur
                    if numeros_consecutifs_2(tirage,suite_3): # Si deux numéros consécutifs on supprime le tirage
                        if nb_paire(tirage,parite): # Si un tirage ne contient pas le nombre de numéro paire voulu par l'utilisateur il sera retiré
                            if def_somme(tirage,somme):# Si la somme des num"ros du tirage correspond à la fourchette voulue par l'utilisateur on conserve le tirage
                                tirage.append(boule_chance)
                                temp_df = pd.DataFrame({'N1':tirage[0],'N2':tirage[1],'N3':tirage[2],
                                                       'N4':tirage[3],'N5':tirage[4],'NChance':tirage[5]},index=[0])
                                
                                jeux_df = pd.concat([jeux_df, temp_df], ignore_index=True)
                                count+=1
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   Affichage des combinaisons restantes
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
st.markdown("---")
st.subheader("Combinaisons restantes :")
st.dataframe(jeux_df)



#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   Creation de la side bar pour afficher logo,date,nombre de combinaisons...
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
st.sidebar.markdown("<h1 style='text-align: center; color: red;'>Proto pour le loto</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("<h2 style='text-align: center;'>Dernier tirage enregistré :</h2>", unsafe_allow_html=True)
jour = data.iloc[0,1]
date = data.iloc[0,2]
st.sidebar.markdown(f"<h3 style='text-align: center; color: blue;'>{jour} {date}</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")


st.sidebar.write(f"<h3 style='text-align: center; color: green;'>Avec votre selection il vous reste {count} combinaisons</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("<h2 style='text-align: center;'>Téléchargez vos combinaisons pour le prochain tirage :</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col2:
    st.sidebar.download_button(label="Sauvegarde des combinaisons",
                        data=jeux_df.to_csv().encode('utf-8'),
                        file_name='csv_clean.csv',
                        mime='text/csv',
                        )
st.sidebar.markdown("---")
st.sidebar.markdown("<h2 style='text-align: center;'>Mettez votre fichier pour le comparer avec le dernier tirage :</h2>", unsafe_allow_html=True)



#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   IA NON SUPERVIEE PERMETTANT DE REDUIRE ENCORE LE NOMBRE DE COMNBINAISON
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   SAUVEGARDE DES COMBINAISONS DANS UN CSV
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#   COMPARAISON ET RAPPORT DU CSV AVEC UN TIRAGE
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


