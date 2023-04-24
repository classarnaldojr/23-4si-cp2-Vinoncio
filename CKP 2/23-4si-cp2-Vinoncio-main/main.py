import cv2
import mediapipe as mp

# Inicializar o módulo de detecção de mãos do mediapipe
mp_maos = mp.solutions.hands
detector_maos = mp_maos.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Iniciar o vídeo
vid = cv2.VideoCapture(0)

# Eu regulei pra funcionar com as minhas mãos, por algum motivo no vídeo sempre dá pedra, talvez porque as proporções da imagem sejam pequenas 
# Mas o da vida real funciona bonitinho!
#vid = cv2.VideoCapture(r"C:\Users\vinic\Documents\FIAP\2023\AI Engineering Cognitive and Semantic Computation IOT\CKP 2\23-4si-cp2-Vinoncio-main\pedra-papel-tesoura.mp4")

# Por algum motivo eu tive que setar o limite porque estava crashando a câmera
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 680)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Função do Detector de mãos
def detector(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    maos = detector_maos.process(frame_rgb)
    return maos

# Opções de jogadas
# PPT = Pedra Papel Tesoura
ppt = {0:"Pedra",1:"Papel",2:"Tesoura",3:"N/A"}

# Função que comapra as mãos e dá um resultado com base nos pontos chave da mão
def comparador_maos(mao):
    pontos = mao.landmark
    ponta_indicador = pontos[8]
    #base_indicador = pontos[5]
    ponta_medio = pontos[12]
    #base_medio = pontos[9]
    ponta_anelar = pontos[16]
    #base_anelar = pontos[13]
    ponta_mindinho = pontos[20]
    #base_mindinho = pontos[17]
    ponta_dedao = pontos[4]
    #base_dedao = pontos[1]
    pulso = pontos[0]

    dedao_pulso = ((ponta_dedao.x - pulso.x)**2 + (ponta_dedao.y - pulso.y)**2)**(1/2)
    indicador_pulso = ((ponta_indicador.x - pulso.x)**2 + (ponta_indicador.y - pulso.y)**2)**(1/2)
    medio_pulso = ((ponta_medio.x - pulso.x)**2 + (ponta_medio.y - pulso.y)**2)**(1/2)
    anelar_pulso = ((ponta_anelar.x - pulso.x)**2 + (ponta_anelar.y - pulso.y)**2)**(1/2)
    mindinho_pulso = ((ponta_mindinho.x - pulso.x)**2 + (ponta_mindinho.y - pulso.y)**2)**(1/2)

    # Alguem me ajuda por favor eu não aguento mais essa lógica não funciona por nada

    # Determinar a jogada com base nas distâncias
    # Resultado Pedra:
    if abs(dedao_pulso) <= 0.2 and abs(medio_pulso) <= 0.2 and abs(indicador_pulso) <= 0.2:
        return ppt[0]
    # Resultado Papel:
    elif abs(dedao_pulso) >= 0.2 and abs(medio_pulso) >= 0.2 and abs(indicador_pulso) >= 0.2 and abs(mindinho_pulso) >= 0.2:
        return ppt[1]
    # Resultado Tesoura
    elif abs(dedao_pulso) <= 0.2 and abs(medio_pulso) >= 0.2 and abs(indicador_pulso) >= 0.2 and abs(anelar_pulso) <= 0.2:
        return ppt[2]
    # N/A
    else:
        return ppt[3]
    
    # Funcionou
    
# Função para determinar o vencedor
def comparar_resultados(res_j1, res_j2):
    vitoria_j1 = (res_j1 == "Pedra" and res_j2 == "Tesoura")or(res_j1 == "Papel" and res_j2 == "Pedra")or(res_j1 == "Tesoura" and res_j2 == "Papel")
    vitoria_j2 = (res_j2 == "Pedra" and res_j1 == "Tesoura")or(res_j2 == "Papel" and res_j1 == "Pedra")or(res_j2 == "Tesoura" and res_j1 == "Papel")
    
    # Resultado Vitória Jogador 1
    if (vitoria_j1):
        return "J1 Ganhou!"
    # Resultado Vitória Jogador 2
    elif (vitoria_j2):
        return "J2 Ganhou!"
    # Resultado Empate:
    else:
        return "Empate :("
    

# O Loop que fará tudo acontecer.
while True:
    ret, frame = vid.read()
    if not ret:
        break
    
    # Detectar as mãos
    detectado = detector(frame)
    
    if detectado.multi_hand_landmarks:
        # Puxando os pontos da mão
        maos = detectado.multi_hand_landmarks
        # Deixando nulo pra não dar pau
        ppt_j1 = None
        ppt_j2 = None
        
        for mao in maos:
            # Determinar a jogada para cada mão
            jogada_ppt = comparador_maos(mao)
            # Achar a mão
            x, y = int(mao.landmark[0].x * frame.shape[1]), int(mao.landmark[0].y * frame.shape[0])
            # Mostrar todos os pontos da mão
            for lm in mao.landmark:
                x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            
            # Definir qual jogador fez a jogada
            if not ppt_j1:
                ppt_j1 = jogada_ppt
            else:
                ppt_j2 = jogada_ppt
        
        # Definir resultado da partida
        if ppt_j1 and ppt_j2:
            resultado = comparar_resultados(ppt_j1, ppt_j2)
            # Desenhar as jogadas na tela
            cv2.putText(frame, f"J1: {ppt_j1}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            cv2.putText(frame, f"J2: {ppt_j2}", (350, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            cv2.putText(frame, resultado, (10, 450), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
        
    # Tudo que abre uma hora tem que fechar né    
    cv2.imshow("Vinicius Joaquim - RM84296 - CKP2", frame)
    # Escondi meu nome no título do vídeo
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()

# Finalmente meu deus do céu são 23:53 eu estou aqui há 6 horas eu preciso dormir