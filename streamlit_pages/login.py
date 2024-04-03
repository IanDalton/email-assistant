#from streamlit_pages import preferences
import streamlit as st
import pandas as pd
from mail.inbox import Inbox
from mail.mail import Mail
from chat.chat import Chatbot

def alta(nombre:str,email:str,legajo:int):
    if "@itba.edu.ar" not in email:
        return False
    try:
        legajo = int(legajo)
    except:
        return False
    
    print(f"Alta de {nombre} con email {email} y legajo {legajo}")
    return True
def baja(nombre:str,email:str,legajo:int):
    if "@itba.edu.ar" not in email:
        return False
    try:
        legajo = int(legajo)
    except:
        return False
    print(f"Baja de {nombre} con email {email} y legajo {legajo}")
    return True
def get_perk_info(perk:str):
    return f"Info de perk {perk}: El {perk} es un beneficio que se le otorga a los empleados de la empresa, cuesta 500$ mensuales y te permite votar en alemania"

def generate_dropdown(dictionary, prefix='', level=0):
    options = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # If the value is a dictionary, recurse on it
            if 'enabled' in value:
                options.append(f'{"-" * level * 4}{prefix}{key}')
            options.extend(generate_dropdown(value, prefix=f'{prefix}{key}/', level=level+1))
    return options

def main(api_key_old=None,email_old=None,app_password_old=None):     
    st.title('App Login')

    # Verify if the user is already logged in
    # Try to fetch the data from the state
    if api_key_old is None:
        api_key_old = st.session_state.get('api_key', '')
    if email_old is None:
        email_old = st.session_state.get('email', '')
    if app_password_old is None:
        app_password_old = st.session_state.get('app_password', '')

    # Create the input fields
    api_key = st.text_input("Enter your API key", type="password",value = api_key_old)
    email = st.text_input("Enter your email", value=email_old)
    app_password = st.text_input("Enter your app password", type="password",value=app_password_old)

    if api_key and email and app_password:
        try:
            if app_password_old != app_password or email_old != email or api_key_old != api_key:
                st.session_state.pop('inbox', None)
                st.session_state.pop('chatbot', None)
                
            if 'inbox' not in st.session_state:
                st.session_state['inbox'] = Inbox( email, app_password,"imap.gmail.com","INBOX")
                st.session_state['email'] = email
                st.session_state['app_password'] = app_password
            
            inbox:Inbox = st.session_state['inbox']
            if 'chatbot' not in st.session_state:
                st.session_state['chatbot'] = Chatbot(api_key,
                  "Sos Esteban Quito miembro del centro de estudiantes del ITBA (CEITBA).",
                  [alta,baja,get_perk_info],
                  [
                      "Tenes que responder correos electronicos administrando bajas y altas, cuando ocurra una baja tenes que llamar a la funcion baja(nombre:str,email:str,legajo:int), lo mismo para alta(nombre:str,email:str,legajo:int). ",
                      "Para procesaro una alta/baja, estos correos si o si tienen que tener el dominio @itba.edu.ar",
                      " Si el usuario pide darse de alta/baja y no tenes toda la informacion, tenes que pedirselo.",
                      "Si el usuario pide informacion de alguno de nuestros beneficios respondele con lo que devuelva la funcion get_perk_info.",
                      "Siempre termina el mail enviandole el linktr.ee del CEITBA. linktr.ee/ceitba y el instagram @ceitba. "
                      "Si vas a dar alta o baja, revisa que tengas el nombre completo de la persona. Este va a estar en el from: antes del correo",
                      "Responde siempre con el primer nombre, no uses el nombre completo",
                      "El correo y el nombre completo lo tenes siempre a menos que te escriban por un correo por fuera del dominio itba.edu.ar",
                      "El legajo es un numero de 5 digitos que puede estar en el cuerpo del correo, es obligatorio para las bajas y altas",
                      "La funcion de alta o baja va a devolver True si se pudo realizar la operacion y False si no se pudo",
                      "Si es una cadena de mails probablemente la informacion relevante este en un mail antiguo",
                      "Mientras no sea una alta o baja, podes responder a una persona con un mail fuera de la organizacion, pero siempre termina con el linktr.ee y el instagram del CEITBA",
                  ]
                  )
                st.session_state['api_key'] = api_key
            
            chatbot:Chatbot = st.session_state['chatbot']
            chatbot.check_key()
        except Exception as e:
            st.error(f'Access denied. Please check your credentials.\n{e}')
        else:
            
            st.success('Access granted. Welcome to the app!')
            # Rest of the app goes here
            st.title('Chatbot')
            st.write('This is a chatbot that will help you answer emails. You can use it to generate answers to emails and send them.')
            personality = st.text_input("Personality")
            rules = ""
            rules = st.text_area("Rules",height=rules.count('\n')+1)
            chatbot.set_personality(personality)
            chatbot.set_instructions(rules)

            
            st.title('Emails')
            tags = generate_dropdown(inbox.fetch_tags())
            options = ['INBOX'] + [tag for tag in tags if tag != 'INBOX']
            col = st.columns(2)
            with col[0]:
                selected_option = st.selectbox('Select a tag', options)
            with col[1]:
                st.write('\n\n')
                st.write('')
                unread = st.checkbox('Show only unread emails',value=True)

            inbox.change_inbox(selected_option)

            if st.button('Fetch emails', key='FetchEmailsButton'):
                inbox.fetch_mail(criteria="UNSEEN" if unread else "ALL")
            mail: Mail
            for mail in list(inbox.mails.values()):
                with st.container(border=True):
                    cols = st.columns([4, 1])  # Create two columns. Adjust the ratio as needed.
                    response = None
                    # Use the first column for the email content.
                    with cols[0]:
                        st.markdown(f"**From:** {mail.mail_from}")
                        st.markdown(f"**Subject:** {mail.subject}")
                        st.markdown(f"**Date:** {mail.date}")
                        st.markdown(f"**Body:** {mail.body}")

                    # Use the second column for the buttons.
                    with cols[1]:
                        if st.button('Generate answer', key=f'ReplyButton_{mail.id}'):
                            with st.spinner('Generating answer...'):
                                chat = chatbot.new_chat()
                                response = chat.send_message(content=f"nombre completo y correo: {mail.mail_from}, Tema: {mail.subject}, contenido:{mail.body}")
                                st.session_state[f'response_{mail.id}'] = response
                        if st.button('Flag', key=f'TagButton_{mail.id}'):
                            # Code to tag the email goes here.
                            mail.add_tag("Flagged")
                            pass
                    response = st.session_state.get(f'response_{mail.id}')
                    if response:
                        cols = st.columns([4, 1])
                        with cols[0]:
                            st.markdown(f"**Response:** {response.parts[0].text}")
                        with cols[1]:
                            if st.button('Send', key=f'SendButton_{mail.id}'):
                                mail.respond(response.parts[0].text)
                                del inbox.mails[mail.id]
                                st.rerun()
                                


    else:
        st.warning('Please enter all the required information to access the app.')

if __name__ == "__main__":
    main()