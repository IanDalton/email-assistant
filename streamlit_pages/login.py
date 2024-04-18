#from streamlit_pages import preferences
import streamlit as st
import pandas as pd
from mail.inbox import Inbox
from mail.mail import Mail
from chat.chat import Chatbot
import asyncio
import nest_asyncio
nest_asyncio.apply()


async def generate_answer(mail,chatbot):
    chat = chatbot.new_chat()
    response = chat.send_message(content=f"nombre completo y correo: {mail.mail_from}, Tema: {mail.subject}, contenido:{mail.body}")
    st.session_state[f'response_{mail.id}'] = response

async def send_answer(mail,response,inbox):
    mail.respond(response.parts[0].text)
    del inbox.mails[mail.id]
    st.rerun()

def alta(nombre:str,email:str,legajo:int):
    if "@itba.edu.ar" not in email:
        return False
    try:
        legajo = int(legajo)
    except:
        return False
    
    print(f"Alta de {nombre} con email {email} y legajo {legajo}")
    with open("altas.csv","a") as f:
        f.write(f"\n{nombre},{email},{legajo}")
        
    return True
def baja(nombre:str,email:str,legajo:int):
    if "@itba.edu.ar" not in email:
        return False
    try:
        legajo = int(legajo)
    except:
        return False
    print(f"Baja de {nombre} con email {email} y legajo {legajo}")
    with open("bajas.csv","a") as f:
        f.write(f"\n{nombre},{email},{legajo}")
    return True
def get_perk_info(perk:str):
    perks = {
        "gympass": """Es un beneficio para miembros del ceitba.
        Acceso a gimnasios y estudios: Con una suscripción mensual única, externa, puedes acceder a diferentes gimnasios y estudios sin contratos ni costos adicionales. Cada plan ofrece 1 check-in diario en la categoría de acceso estándar para acceder a gimnasios y estudios asociados, ya sea presencialmente o en línea.
Apps Asociadas ilimitadas: Además, la suscripción incluye acceso a aplicaciones asociadas que ofrecen actividades como meditación, nutrición, terapia y sesiones personales en línea.
Beneficios para colaboradores/as:
Mayor actividad física: Fomenta un mayor nivel de actividad física con gimnasios y estudios presenciales.
Bienestar emocional: Alivia el estrés y promueve el cuidado personal con apps para el bienestar emocional.
Nutrición saludable: Promueve hábitos alimentarios saludables con apps de nutrición.
Flexibilidad: Ofrece acceso flexible al bienestar con clases on demand.
Red de Bienestar:

Más de 50,000 gimnasios y estudios presenciales.
Más de 2,500 entrenadores personales online.
Más de 2,000 apps y clases on demand.""",

    }
    perk = perk.lower().strip()
    if perk not in perks:
        return False
    return perks[perk]
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
                      "Cuando llamas a la funcion get_perk_info esta te va a devolver un string con la informacion o un False si es que no tiene.",
                      "Por ahora el unico perk que ofrecemos es gympass",
                      "Cuando tengas la informacion del perk responde de forma natural la informacion que te devuelva la funcion get_perk_info",
                      "No uses markdown para las respuestas",
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
            personality = st.text_input("Personality",value=chatbot.personality)
            rules = ""
            rules = st.text_area("Rules",height=rules.count('\n')+1,value="\n".join(chatbot.instructions))
            chatbot.set_personality(personality)
            chatbot.set_instructions(rules)

            
            st.title('Emails')
            tags = generate_dropdown(inbox.fetch_tags())
            options = ['INBOX'] + [tag for tag in tags if tag != 'INBOX']
            unread = True
            col = st.columns(2)
            with col[0]:
                selected_option = st.selectbox('Select a tag', options)
                if st.button('Fetch emails', key='FetchEmailsButton'):
                    inbox.fetch_mail(criteria="UNSEEN" if unread else "ALL")
            with col[1]:
                st.write('\n\n')
                st.write('')
                unread = st.checkbox('Show only unread emails',value=True)
                if st.button('Generate answers for all emails', key='GenerateAllAnswersButton'):
                    loop = asyncio.get_event_loop()
                    tasks = [loop.create_task(generate_answer(mail, chatbot)) for mail in list(inbox.mails.values())]
                    loop.run_until_complete(asyncio.gather(*tasks))
                    st.rerun()
                if st.button('Send answers for all emails', key='SendAllAnswersButton'):
                    loop = asyncio.get_event_loop()
                    tasks = [loop.create_task(send_answer(mail, st.session_state[f'response_{mail.id}'], inbox)) for mail in list(inbox.mails.values())]
                    loop.run_until_complete(asyncio.gather(*tasks))
                    st.rerun()

            inbox.change_inbox(selected_option)
            
            


                
           
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