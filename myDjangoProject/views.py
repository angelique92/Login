from django.shortcuts import render
from .forms import IdentForm
from .models import Ident, Log
from django.utils import timezone
import datetime
import re
import hashlib
from django.views.decorators.csrf import csrf_exempt
import sqlite3 

# Fonction qui gère les différentes intéraction sur la page html
@csrf_exempt
def index(request):
    if request.method == 'POST':

        # L' utilisateur a cliquer sur le bouton Connect ->
            # Vérifie si l'utilisateur peut se connecter
            # Vérification du pseudo et du mot de passe dans la database
        if "btn_connect" in request.POST:

            form = IdentForm(request.POST)
            field = form.fields['Password2']
            field.widget = field.hidden_widget()
            if form.is_valid():
                print("Username :", form.cleaned_data['Username'])

                mdp= form.cleaned_data['Password']
                name = form.cleaned_data['Username']
                print("mdp :", mdp, "name :", name)

                if request.POST.get('Username') == "":
                    return render(request,
                                  'myDjangoProject/templates/login.html', {'form': form, "error": "The Username  cant be none."})
                if request.POST.get('Password') == "":
                    return render(request,
                                  'myDjangoProject/templates/login.html', {'form': form, "error": "The Password  cant be none."})
                else:
                    mdp_chiffree=chiffrement_password_md5(mdp)
                    result_user_n_pass=Ident.objects.filter(Username=form.cleaned_data['Username'], Password=mdp_chiffree ).exists()
                    result_false_username=Ident.objects.filter(Username=form.cleaned_data['Username']).exists()

                    if is_user_block(name):
                        time=how_much_time_block(name)
                        return render(request,
                                      'myDjangoProject/templates/login.html',
                                      {'form': form, "error": "The User " + name + " is already block until "+ str(time.strftime("%m/%d/%Y, %H:%M:%S")  ) })

                    if result_user_n_pass == True:
                        save_login_request(name,mdp_chiffree , "sucess")
                        return render(request,
                                      'myDjangoProject/templates/connect_page.html',{"info": "The User  is connect"})
                    if result_false_username == False:
                        return render(request,
                                      'myDjangoProject/templates/login.html', {'form': form, "error": "The Username  does not exist."})
                    if result_user_n_pass== False and result_false_username==True:
                        save_login_request(name, mdp, "echec")
                        if is_3_echecs(name) == False:
                            return render(request,
                                          'myDjangoProject/templates/login.html', {'form': form,"error": "The Password  is incorrect."})
                        else:
                            time = how_much_time_block(name)
                            return render(request,
                                          'myDjangoProject/templates/login.html',
                                          {'form': form, "error": "The User " +name + " is block until "+str(time.strftime("%m/%d/%Y, %H:%M:%S")  ) })
                    if result_username == False:
                        delete_utilisateur(name)
        # L' utilisateur a cliquer sur le bouton Add ->
            # Envoie sur la page de création de compte
        if "btn_add" in request.POST:
            print("L'utilisateur a appuyer sur le bouton ADD")
            form = IdentForm()
            return render(request,'myDjangoProject/templates/create_compte.html', {'form': form})
        
        # Rajout du bouton delete
        if "btn_delete" in request.POST:
            print("A cliquer sur supp account")
            form = IdentForm()
            return render(request,'myDjangoProject/templates/delete.html', {'form': form})
        
        if "save_delete" in request.POST: 
            print("L'utilisateur a appuyer sur le bouton delete account ")
            if request.POST.get('Password') ==  "":
                form = IdentForm(request.POST)
                return render(request,
                              'myDjangoProject/templates/delete.html',
                              {'form': form, "error": "The Password  can't be none."})
            if request.POST.get('Password') == request.POST.get('Password2'):
                form = IdentForm(request.POST)
                if form.is_valid():
                    mdp = form.cleaned_data['Password']
                    name = form.cleaned_data['Username']
                    print("Fonction index Name : ", name)
                    result_password = password_check(mdp)
                    result_username = Ident.objects.filter(Username=form.cleaned_data['Username']).delete()
                    if result_username == False:
                        return render(request,
                                      'myDjangoProject/templates/delete.html',
                                      {'form': form, "error": "The Username  is not the good one"})
                    elif result_password == False:
                        form = IdentForm(request.POST)
                        return render(request,
                                      'myDjangoProject/templates/delete.html',
                                      {'form': form, "error": "One of this password is not right"})

                    elif result_password == True and result_username == True :
                        result_user_n_pass = Ident.objects.filter(Username=form.cleaned_data['Username'],Password=form.cleaned_data['Password']).delete()
                        return render(request,
                                  'myDjangoProject/templates/delete.html' , {"info": "The User is delete Sucessfully"})
            else:
                form = IdentForm(request.POST)
                return render(request,
                              'myDjangoProject/templates/delete.html',
                              {'form': form,"error": "The Password are not matching"})



        # L' utilisateur a cliquer sur le bouton Save ->
            # Verification
                # que les champs ne sont pas vide
                # Pseudo n'existe pas
                # Mot de passe fort
            # Encodage du mot de passe dans la database
        if "btn_save" in request.POST:
            print("L'utilisateur a appuyer sur le bouton SAVE")
            if request.POST.get('Username') ==  "":
                form = IdentForm(request.POST)
                return render(request,
                              'myDjangoProject/templates/create_compte.html',
                              {'form': form, "error": "The Username  can't be none."})
            if request.POST.get('Password') == request.POST.get('Password2'):
                form = IdentForm(request.POST)
                if form.is_valid():
                    mdp = form.cleaned_data['Password']
                    name = form.cleaned_data['Username']
                    print("Fonction index Name : ", name)
                    result_password = password_check(mdp)
                    result_username = Ident.objects.filter(Username=form.cleaned_data['Username']).exists()
                    if result_username == True:
                        return render(request,
                                      'myDjangoProject/templates/create_compte.html',
                                      {'form': form, "error": "The Username  already exist."})
                    elif result_password == False:
                        return render(request,
                                      'myDjangoProject/templates/create_compte.html',
                                      {'form': form, "error": "The Password is too easy"})

                    elif result_password == True and result_username == False :
                        new_mdp= chiffrement_password_md5(form.cleaned_data['Password'])
                        #form = IdentForm(initial={'Username': name, 'Password':new_mdp})
                        author = form.save(commit=False)
                        author.Password = new_mdp
                        author.Password2 = new_mdp
                        author.save()
                        #form.save()
                        return render(request,
                                  'myDjangoProject/templates/connect_page.html' , {"info": "The User  is created Sucessfully"})
                else:
                    return render(request,
                                  'myDjangoProject/templates/connect_page.html',
                                  {"error": "form invalid"})
            else:
                form = IdentForm(request.POST)
                return render(request,
                              'myDjangoProject/templates/create_compte.html',
                              {'form': form,"error": "The Password are not matching"})


        # L' utilisateur a cliquer sur le bouton Reset ou Back ->
            # Renvoie la page principale de login avec les champs vide
        elif "btn_reset" in request.POST:
            print("L'utilisateur a appuyer sur le bouton RESET ou Back")
            form = IdentForm()
            field = form.fields['Password2']
            field.widget = field.hidden_widget()
            return render(request,
                          'myDjangoProject/templates/login.html',
                          {'form': form})
        
        elif "btn_back" in request.POST:
            print("L'utilisateur a appuyer sur le bouton RESET ou Back")
            form = IdentForm()
            field = form.fields['Password2']
            field.widget = field.hidden_widget()
            return render(request,
                          'myDjangoProject/templates/login.html',
                          {'form': form})
        


    else:
        form = IdentForm()
        field = form.fields['Password2']
        field.widget = field.hidden_widget()
    return render(request,
                  'myDjangoProject/templates/login.html',
                  {'form': form})  # passe ce formulaire au gabarit


#Verifie que le mot de passe est compliqué
def password_check(password):
    while True:
        if type(password) != str:
            flag = False
            break
        if (len(password) <= 8):
            flag = False
            break
        elif not re.search("[a-z]", password):
            flag = False
            break
        elif not re.search("[A-Z]", password):
            flag = False
            break
        elif not re.search("[0-9]", password):
            flag = False
            break
        elif re.search("\s", password):
            flag = False
            break
        else:
            flag = True
            print("Valid Password")
            break

    if flag == False:
        print("Not a Valid Password ")
    return flag


# Chiffrement d'un mot de passe avec la méthode MD5
def chiffrement_password_md5(mdp):
    md5_hash = hashlib.md5()
    md5_hash.update(mdp.encode())
    print("Le mdp en clair :", mdp)
    print("Le mdp chiffré : ", md5_hash.hexdigest())
    return md5_hash.hexdigest()

# Sauvegarde chaque connection dans la Database
def save_login_request(name, password,connect):
    p = Log(Username=name, Password=password, Date= datetime.datetime.now(), Connection=connect,Is_delete=False,Date_retard=datetime.datetime.now() )
    p.save()
    if connect == True:
        delete_log(name)

# Verifie que l'utilisateur est bloquer
    # Si il est bloqué la fonction vérifie le temps du blocage
    # La fonction renvoie True si le délais n'est pas dépassé
    # Renvoie False si l'utilisateur est débloqué
def is_user_block(name):
    user_block=Log.objects.filter(Username=name, Connection="block", Is_delete=False).exists()
    if user_block == True:
        user=Log.objects.filter(Username=name, Connection="block").last()
        obj = user
        field_object = Log._meta.get_field("Date_retard")
        value_retard = field_object.value_from_object(obj)


        print(" value :", value_retard)
        now = timezone.now()
        if value_retard > now:
            return True
        else:
            Log.objects.filter(Username=name, Connection="block", Is_delete=False).update(Is_delete=True)
            Log.objects.filter(Username=name, Connection="echec", Is_delete=False).update(Is_delete=True)
            return False
    return False

# Vérification que l'utilisateur s'est trompé 3 fois de mot de passe
# Si oui alors Blocage de l'utilisateur renvoie True
# Si non False
def is_3_echecs(name):
    liste_number_echecs_username=Log.objects.filter(Username=name, Connection="echec", Is_delete=False).count()

    if liste_number_echecs_username >= 3:
        Log.objects.filter(Username=name, Connection="echec").update(Is_delete=True)
        p = Log(Username=name, Password="", Date=datetime.datetime.now(), Connection="block", Is_delete=False,
                Date_retard=datetime.datetime.now()+datetime.timedelta(seconds=60))
        p.save()

        print("Block user ", name )
        return True

    return False


# Indique le temps de blocage
def how_much_time_block(name):
    user_block = Log.objects.filter(Username=name, Connection="block", Is_delete=False).last()

    field_object = Log._meta.get_field("Date_retard")
    value_retard = field_object.value_from_object(user_block)

    print("La date retard est ", value_retard)
    return value_retard

#Mets la table a jour pour l'utilisateur qui a eu plusieurs echec et blocage
def delete_log(name):
    Log.objects.filter(Username=name, Connection="echec").update(Is_delete=True)
    Log.objects.filter(Username=name, Connection="block").update(Is_delete=True)
    
def delete_utilisateur(name):
    Log.objects.filter(UserWarning=name, Connection="delete").update(Is_delete = True)


#Renvoie la page principale
def connect_page(request):
    return render(request,
                  'myDjangoProject/templates/login.html')

# def delete_page(request):
#     return render(request,
#                   'myDjangoProject/templates/delete.html')