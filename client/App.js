import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState, useRef } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { DOMEN } from './Consts.ts';

export default function App() {
    const [facing, setFacing] = useState('back');
    const [permission, requestPermission] = useCameraPermissions();
    const [isStreaming, setIsStreaming] = useState(false);
    const [emotionDetected, setEmotionDetected] = useState('Не обнаружено');
    const cameraRef = useRef(null);
    const intervalRef = useRef(null);

    if (!permission) {
        // Загрузка разрешений камеры.
        return <View />;
    }

    if (!permission.granted) {
        // Разрешения на камеру еще не предоставлены.
        return (
            <View style={styles.container}>
                <Text style={{ textAlign: 'center' }}>Мы нуждаемся в вашем разрешении для использования камеры</Text>
                <Button onPress={requestPermission} title="Предоставить разрешение" />
            </View>
        );
    }

    function toggleCameraFacing() {
        setFacing(current => (current === 'back' ? 'front' : 'back'));
    }

    const startStreaming = async () => {
        if (!cameraRef.current) {
            console.warn('Камера не готова');
            return;
        }

        setIsStreaming(true);
        intervalRef.current = setInterval(async () => {
            if (cameraRef.current) {
                try {
                    let photo = await cameraRef.current.takePictureAsync({ quality: 0.1, skipProcessing: true });
                    handleEmotionDetection(photo.uri);
                } catch (error) {
                    console.error('Ошибка при создании фото:', error);
                }
            }
        }, 1000); // Захват фотографии каждую секунду
    };


    const stopStreaming = () => {
        setIsStreaming(false);
        clearInterval(intervalRef.current);
    };

    const handleEmotionDetection = async (photoUri) => {
        try {
            const formData = new FormData();
            formData.append('photo', {
                uri: photoUri,
                type: 'image/jpeg',
                name: 'photo.jpg',
            });
            const response = await fetch(`${DOMEN}api/analyze_camera_photo/`, {
                method: 'POST',
                body: formData,
            });
            const { emotion_detected } = await response.json();
            setEmotionDetected(emotion_detected ? 'Плачет' : 'Не плачет');
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <View style={styles.container}>
            <CameraView
                style={styles.camera}
                facing={facing}
                ref={cameraRef}
            >
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
                        <Text style={styles.text}>Поменять камеру</Text>
                    </TouchableOpacity>
                    {!isStreaming ? (
                        <TouchableOpacity style={styles.button} onPress={startStreaming}>
                            <Text style={styles.text}>Начать стрим</Text>
                        </TouchableOpacity>
                    ) : (
                        <TouchableOpacity style={styles.button} onPress={stopStreaming}>
                            <Text style={styles.text}>Остановить стрим</Text>
                        </TouchableOpacity>
                    )}
                </View>
            </CameraView>
            <View style={styles.emotionContainer}>
                <Text style={[styles.emotionText, emotionDetected === 'Плачет' ? styles.greenText : styles.redText]}>
                    Эмоция: {emotionDetected}
                </Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
    },
    camera: {
        flex: 1,
    },
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        position: 'absolute',
        bottom: 20,
        width: '100%',
    },
    button: {
        backgroundColor: '#007AFF',
        padding: 10,
        borderRadius: 5,
    },
    text: {
        fontSize: 18,
        color: 'white',
    },
    emotionContainer: {
        position: 'absolute',
        bottom: 80,
        width: '100%',
        alignItems: 'center',
    },
    emotionText: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
    },
    greenText: {
        color: 'green',
    },
    redText: {
        color: 'red',
    },
});
