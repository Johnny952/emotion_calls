# Detección de emociones en frases de actores

Se utilizan dos datasets MELD y RAVDESS
 
Son 8 sentimientos a predecir


## Configuración del Proyecto
Clonar repositorio: <br/>
```git clone https://github.com/Johnny952/emotion_calls.git``` <br/>
```cd emotion_calls ```

Clonar librería pyAudioAnalysis: <br/>
```git clone https://github.com/tyiannak/pyAudioAnalysis.git```

Instalar Requerimentos: <br/>
``` pip install -r requirements.txt```

## Predecicción de sentimientos en archivo de audio
- Copiar dirección de archivo de audio <br/> 
- Cambiar código ```detect_emotion.py``` con dirección al archivo de audio <br/>
- Ejecutar:<br/>
```python detect_emotion.py```
