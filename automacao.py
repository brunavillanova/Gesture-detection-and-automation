import cv2
import numpy as np
import math

# Inicializa a captura de vídeo
cap = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            continue  # Se não conseguir ler o frame, continue para o próximo loop

        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        # Define a região de interesse (ROI) para análise
        roi = frame[100:300, 100:300]
        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Define os limites da cor da pele em HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # Aplica dilatação e desfoque na máscara
        mask = cv2.dilate(mask, kernel, iterations=4)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        # Encontra os contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cnt = max(contours, key=cv2.contourArea)

            # Aproxima o contorno ao objeto
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # Cria um casco convexo ao redor da mão
            hull = cv2.convexHull(cnt)
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)
            arearatio = ((areahull - areacnt) / areacnt) * 100

            # Encontra os defeitos convexos
            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull) if hull is not None else None

            l = 0

            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(approx[s][0])
                    end = tuple(approx[e][0])
                    far = tuple(approx[f][0])

                    # Calcula o comprimento dos lados do triângulo
                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    s = (a + b + c) / 2
                    ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

                    # Calcula a distância entre o ponto e o casco convexo
                    d = (2 * ar) / a

                    # Calcula o ângulo do ponto em relação ao casco convexo
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                    # Ignora ângulos > 90 e pontos muito próximos ao casco convexo
                    if angle <= 90 and d > 30:
                        l += 1
                        cv2.circle(roi, far, 3, [255, 0, 0], -1)

                    # Desenha linhas ao redor da mão
                    cv2.line(roi, start, end, [0, 255, 0], 2)

            l += 1

            # Imprime gestos correspondentes
            font = cv2.FONT_HERSHEY_SIMPLEX
            if l == 1:
                if areacnt < 2000:
                    cv2.putText(frame, 'Esperando dados', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    if arearatio < 12:
                        cv2.putText(frame, '0 = Navegador', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    elif arearatio < 17.5:
                        cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    else:
                        cv2.putText(frame, '1 = Word', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 2:
                cv2.putText(frame, '2 = Excel', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 3:
                if arearatio < 27:
                    cv2.putText(frame, '3 = Power Point', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 4:
                cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 5:
                cv2.putText(frame, '', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            elif l == 6:
                cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        # Exibe as janelas
        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)
    except Exception as e:
        print(f"Erro: {e}")

    # Sai do loop se a tecla ESC for pressionada
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

# Libera os recursos
cap.release()
cv2.destroyAllWindows()
