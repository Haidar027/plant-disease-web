import os
import base64
import re
import io
import json
import tensorflow as tf
from PIL import Image
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from tensorflow.python.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.optimizers import Adam
from classification.camera import VideoCamera, IPWebCam
from .forms import PlantImageForm
from .utils import save_uploaded_image
import numpy as np
import glob
import requests
import cv2


# Create your views here.

def home(request):
    return render(request, 'home.html')

# Load the trained model
# model = tf.keras.models.load_model('model_combine_v4.h5')

# Load the TensorFlow Lite model
# model_path = os.path.join(settings.BASE_DIR, 'model_combine_v3.tflite')
# interpreter = tf.lite.Interpreter(model_path=model_path)
# interpreter.allocate_tensors()

# Define a dictionary mapping class indices to class names
class_names = {
    0: 'Cassava Bacterial Blight',
    1: 'Cassava Brown Streak Disease',
    2: 'Cassava Green Mottle',
    3: 'Cassava Healthy',
    4: 'Cassava Mossaic Disease',
    5: 'Grape Black Rot',
    6: 'Grape Esca (Black Measles)',
    7: 'Grape Healthy',
    8: 'Grape Leaf Blight',
    9: 'Potato Early Blight',
    10: 'Potato Healthy',
    11: 'Potato Late Blight',
    12: 'Rice Brown Spot',
    13: 'Rice Healthy',
    14: 'Rice Hispa',
    15: 'Rice Leaf Blast',
    16: 'Tomato Bacterial Spot',
    17: 'Tomato Early Blight',
    18: 'Tomato Healthy',
    19: 'Tomato Late Blight',
    20: 'Tomato Leaf Mold',
    21: 'Tomato Mosaic Virus',
    22: 'Tomato Septoria Leaf Spot',
    23: 'Tomato Target Spot',
    24: 'Tomato Two-Spotted Spider Mite',
    25: 'Tomato Yellow Leaf Curl Virus'
}

class_names_cassava = {
    0: 'Cassava Bacterial Blight',
    1: 'Cassava Brown Streak Disease',
    2: 'Cassava Green Mottle',
    3: 'Cassava Healthy',
    4: 'Cassava Mosaic Disease'
}

class_names_tomato = {

}

class_names_potato = {
    0: 'Potato Early Blight',
    1: 'Potato Healthy',
    2: 'Potato Late Blight'
}

class_names_rice = {
    0: 'Rice Brown Spot',
    1: 'Rice Healthy',
    2: 'Rice Hispa',
    3: 'Rice Leaf Blast'
}

class_names_grape = {
    0: 'Grape Black Rot',
    1: 'Grape Esca (Black Measley)',
    2: 'Grape Healthy',
    3: 'Grape Leaf Blight'
}

def classify(request):
    if request.method == 'POST':
        form = PlantImageForm(request.POST, request.FILES)
        if form.is_valid():    
                # Save the uploaded image
                form.save()

                # Get the choosen model
                selected_model = request.POST['model']
                uploaded_image = request.FILES['image']

                # Get the uploaded image from the form
                uploaded_image = form.instance.image

                # if selected_model == 'model_cassava':
                #     model_path = os.path.join(settings.BASE_DIR, 'model_cassava.h5')
                #     current_class_names = class_names_cassava
                # elif selected_model == 'model_tomato':
                #     model_path = os.path.join(settings.BASE_DIR, 'model_tomato.h5')
                #     current_class_names = class_names_tomato
                if selected_model == 'model_potato':
                    model = tf.keras.models.load_model('model_potato_v2.h5')
                    current_class_names = class_names_potato
                elif selected_model == 'model_rice':
                    model = tf.keras.models.load_model('model_rice_v1.h5')
                    current_class_names = class_names_rice
                elif selected_model == 'model_grape':
                    model = tf.keras.models.load_model('model_grape_v2.h5')
                    current_class_names = class_names_grape
                elif selected_model == 'model_combine':
                    model = tf.keras.models.load_model('model_combine_v4.h5')
                    current_class_names = class_names

                # Load selected model
                # model = load_model(model_path)

                # Preprocess the image for model input
                img_upload = image.load_img(uploaded_image.path, target_size=(256, 256))
                img_array = image.img_to_array(img_upload)
                img_array = np.expand_dims(img_array, axis=0)
                img_array /= 255.0

                # Make predictions using the trained model
                predictions = model.predict(img_array)
                predicted_class_index = np.argmax(predictions[0])
                predicted_class = current_class_names[predicted_class_index]
                probability = "{:.2f}".format(predictions[0][predicted_class_index] * 100)

                # Perform inference with the TensorFlow Lite model
                # input_details = interpreter.get_input_details()
                # output_details = interpreter.get_output_details()

                # interpreter.set_tensor(input_details[0]['index'], img_array)
                # interpreter.invoke()
                # predictions = interpreter.get_tensor(output_details[0]['index'])
                # predicted_class_index = np.argmax(predictions)
                # predicted_class = class_names[predicted_class_index]
                # probability = "{:.2f}".format(predictions[0][predicted_class_index] * 100)


                # Define treatment information based on the predicted class
                if predicted_class == 'Cassava Bacterial Blight':
                    treatment = 'Organic Control\nPerendaman benih yang terserang dalam air panas pada suhu 60 derajat celcius selama 20 menit, diikuti dengan pengeringan pada lapisan dangkal pada suhu 30 derajat celcius semalaman atau pada suhu 50 derajat celcius selama 4 jam, mengurangi jumlah bakteri secara signifikan. Benih juga dapat direndam dalam air dan dipanaskan dalam oven microwave hingga suhu air mencapai 73 derajat celcius diikuti dengan pembuangan airnya dengan segera\n\nChemical Control\nselalu pertimbangkan pendekatan terpadu dengan tindakan pencegahan dan pengobatan biologis jika tersedia. saat ini belum ada pengendalian langsung secara kimiawi terhadap penyakit hawar bakteri singkong. '
                    trsource = 'https://plantix.net/en/library/plant-diseases/300039/cassava-bacterial-blight/'
                elif predicted_class == 'Cassava Brown Streak Disease':
                    treatment = 'Organic Control\nTidak ada pengendalian biologis langsung terhadap virus setelah menginfeksi tanaman. Salah satu cara untuk mengurangi penyebaran penyakit ini adalah dengan menahan diri dari penggunaan insektisida yang berlebihan yang dapat merugikan musuh alami kutu daun, tungau, dan lalat putih, yang merupakan vektor CBSV.\n\nChemical Control\nSelalu pertimbangkan pendekatan terpadu dengan tindakan pencegahan bersama dengan biologis jika tersedia. Penyakit virus tidak dapat diobati dengan aplikasi kimia. Namun demikian insektisida dapat digunakan untuk mengurangi populasi vektor seperti lalat putih, tungau, dan kutu daun dan mengurangi terjadinya penyakit.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Cassava Green Mottle':
                    treatment = 'Saat ini belum ada pestisida dan antibiotik yang dapat mengobati Penyakit Bercak Hijau ini. Cara paling efektif untuk mencegah penyakit ini adalah mengontrol lalat putih yang menyebarkannya.'    
                    trsource = 'https://en.wikipedia.org/wiki/Cassava_green_mottle_virus#:~:text=Treatments%3A,the%20whiteflies%20that%20spread%20it.'
                elif predicted_class == 'Cassava Healthy':
                    treatment = 'Tidak perlu penanganan'
                    trsource = '-'
                elif predicted_class == 'Cassava Mossaic Disease':
                    treatment = 'Organic Control\nTidak ada penanganan yang tersedia untuk mengendalikan virus ini. Bagaimanapun juga lalat putih memiliki banyak predator yang dapat digunakan. Cara paling memungkinkan untuk mengendalikan virus ini adalah dengan Isaria Farinosa dan Isaria Fumosorosea.\n\nChemical Control :\nelalu pertimbangkan pendekatan terpadu dengan tindakan pencegahan bersama dengan pengobatan biologis jika tersedia. Bahan aktif yang telah dilaporkan memiliki efek dalam mengendalikan populasi kutu kebul di seluruh dunia termasuk bifenthrin, buprofezin, fenoksikarb, deltametrin, azidirachtin, dan pymetrozine. Namun, gunakanlah produk-produk ini dengan bijaksana, karena penggunaan yang tidak tepat sering kali menyebabkan perkembangan resistensi pada serangga.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Grape Black Rot':
                    treatment = 'Organic Control\nSegera setelah memasuki tahap mekar, Anda dapat menyemprotkan Bacillus thuringiensis.\n\nChemical Control\naplikasi bahan kimia dilakukan dengan cara pencegahan. Penyemprotan strat kira-kira dua minggu sebelum mekar dengan captan + mycobutanil atau mancozeb + mycobutanil. Tepat sebelum bunga mekar, Anda juga dapat menggunakan karbaril atau imidakloprid. Semprotan pasca-mekar mancozeb + mycobutanil, imidacioprid atau azadirachtin. Sepuluh hari setelah mekar, Anda juga dapat menggunakan campuran captan dan belerang pada tanaman merambat Anda. Karena sebagian besar varietas anggur menjadi kebal terhadap infeksi tiga hingga empat minggu setelah mekar, semprotan kimiawi harus dihindari pada saat itu.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Grape Esca (Black Measles)':
                    treatment = 'Esca dianggap sebagai penyakit batang dan setidaknya menurut orang Italia, penyakit ini harus ditangani dengan cara yang sama seperti Anda menangani penyakit Eutypa atau Botryosphaeria dieback. Hindari membuat potongan besar selama pemangkasan dan jangan memangkas selama periode kelembaban tinggi. Tutuplah luka-luka atau semprotkan fungisida setelah pemangkasan.'
                    trsource = 'https://advancedvit.com/esca/#:~:text=Esca%20is%20considered%20a%20trunk,or%20spray%20fungicide%20post%2Dpruning.'
                elif predicted_class == 'Grape Healthy':
                    treatment = 'Tidak perlu penanganan'
                    trsource = '-'
                elif predicted_class == 'Grape Leaf Blight':
                    treatment = 'Penyakit ini dapat diatasi secara efektif melalui kombinasi penggunaan kultur, sanitasi, resistensi, dan semprotan fungisida. Pendekatan terpadu untuk pengendalian penyakit ini meminimalkan ketergantungan pada satu jenis pengendalian di atas yang lain dan biasanya menghasilkan persentase yang tinggi dari buah berkualitas.'
                    trsource = 'https://vikaspedia.in/agriculture/crop-production/integrated-pest-managment/ipm-for-fruit-crops/ipm-strategies-for-grapes/grapes-diseases-and-symptoms#:~:text=Symptoms%20of%20this%20disease%20are,eventually%20turn%20brown%20and%20die.'
                elif predicted_class == 'Potato Early Blight':
                    treatment = 'Penyakit ini dapat diminimalisir dengan menjaga kondisi pertumbuhan yang optimal, termasuk pemupukan yang tepat, irigasi, dan pengelolaan hama lainnya. Tanamlah varietas yang berumur lebih tua dan musimnya lebih panjang. Penggunaan fungisida hanya dibenarkan jika penyakit ini muncul cukup dini sehingga menyebabkan kerugian ekonomi.'
                    trsource = 'https://ipm.ucanr.edu/agriculture/potato/early-blight/#:~:text=Early%20blight%20can%20be%20minimized,enough%20to%20cause%20economic%20loss.'
                elif predicted_class == 'Potato Healthy':
                    treatment = 'Tidak perlu penanganan'
                    trsource = '-'
                elif predicted_class == 'Potato Late Blight':
                    treatment = 'Penyakit busuk daun dikendalikan dengan menghilangkan tumpukan cull dan kentang sukarela, menggunakan praktik pemanenan dan penyimpanan yang tepat, dan menggunakan fungisida bila perlu. Drainase udara untuk memfasilitasi pengeringan dedaunan setiap hari adalah penting.'
                    trsource = 'https://ipm.ucanr.edu/agriculture/potato/late-blight/#:~:text=Late%20blight%20is%20controlled%20by,foliage%20each%20day%20is%20important.'
                elif predicted_class == 'Rice Brown Spot':
                    treatment = 'Gunakan fungisida (misalnya, iprodione, propikonazol, azoksistrobin, trifloksistrobin, dan karbendazim) sebagai perawatan benih. Rawat benih dengan air panas (53-54°C) selama 10-12 menit sebelum ditanam, untuk mengendalikan infeksi primer pada tahap pembibitan.'    
                    trsource = 'http://www.knowledgebank.irri.org'
                elif predicted_class == 'Rice Healthy':
                    treatment = 'Tidak perlu penanganan'
                    trsource = '-'
                elif predicted_class == 'Rice Hispa':
                    treatment = 'Organic Control\nPengendalian biologis hama ini masih dalam penelitian. Parasitoid larva, Eulophus femoralis telah diperkenalkan di Bangladesh dan India dan dapat mengurangi masalah hispa di daerah-daerah ini. Konservasi musuh alami asli juga dapat memainkan peran penting dalam pengelolaan hama ini. Sebagai contoh, ada tawon kecil yang menyerang telur dan larva serta serangga reduviid yang memakan serangga dewasa. Selain itu, ada juga tiga patogen jamur yang menyerang hama dewasa.\n\nChemical Control\nSelalu pertimbangkan pendekatan terpadu dengan tindakan pencegahan bersama dengan perawatan biologis jika tersedia. Dalam kasus serangan yang parah, beberapa formulasi kimiawi yang mengandung bahan aktif berikut ini dapat digunakan untuk mengendalikan populasi: klorpirifos, malation, cypermethrin, fenthoate.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Rice Leaf Blast':
                    treatment = 'Organic Control\nHingga saat ini, belum ada pengendalian biologis yang efektif untuk penyakit ini yang tersedia secara komersial. Eksperimen sedang berlangsung untuk menguji kelayakan produk berdasarkan bakteri Streptomyces atau Pseudomonas pada fungsu dan kejadian atau penyebaran penyakit.\n\nChemical Control\nPerawatan benih dengan thiram efektif untuk melawan penyakit ini. Fungisida yang mengandung azoxystrobin, atau bahan aktif dari famili triazol atau strobilurin juga dapat disemprotkan pada tahap pembibitan, anakan, dan kemunculan malai untuk mengendalikan penyakit blas. Satu atau dua kali aplikasi fungisida pada saat tanam bisa efektif untuk mengendalikan penyakit ini.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Tomato Bacterial Spot':
                    treatment = 'Organic Control\nBacterial Spot sangat sulit dikendalikan dan juga mahal untuk diobati. Jika penyakit ini muncul di awal musim, pertimbangkan untuk memusnahkan seluruh tanaman. Bakterisida yang mengandung tembaga memberikan lapisan pelindung pada dedaunan dan buah untuk kedua bakteri tersebut. Virus bakteri (bakteriofag) yang secara khusus membunuh bakteri tersedia untuk mengatasi bercak bakteri. Perendaman benih selama satu menit dalam natrium hipokiorit atau dalam air panas (50 derajat celcius) selama 25 menit dapat mengurangi kejadian kedua penyakit tersebut.\n\nChemical Control\nBakterisida yang mengandung tembaga dapat digunakan sebagai pelindung dan memberikan pengendalian penyakit secara parsial. Aplikasi pada saat gejala awal penyakit dan kemudian pada interval 10 hingga 14 hari ketika kondisi hangat (bercak) atau dingin (bintik) dan lembab. Karena perkembangan resistensi terhadap tembaga sering terjadi, kombinasi bakterisida berbasis tembaga dengan mancozeb juga direkomendasikan.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Tomato Early Blight':
                    treatment = 'Jika penyakit busuk daun telah menyebar ke lebih dari beberapa daun tanaman, gunakan Fungisida Siap Pakai, yang membunuh spora jamur dan mencegah penyakit busuk daun menyebabkan kerusakan lebih lanjut.'
                    trsource = 'https://www.gardentech.com/blog/pest-id-and-prevention/fight-blight-on-your-tomatoes#:~:text=If%20blight%20has%20already%20spread,blight%20from%20causing%20further%20damage.'
                elif predicted_class == 'Tomato Healthy':
                    treatment = 'Tidak perlu penanganan'
                    trsource = '-'
                elif predicted_class == 'Tomato Late Blight':
                    treatment = 'Organic Control\nPada saat ini, tidak ada pengendalian biologis yang diketahui efektif melawan penyakit busuk daun. Untuk menghindari penyebaran, segera cabut dan hancurkan tanaman di sekitar tempat yang terinfeksi dan jangan membuat kompos dari bahan tanaman yang terinfeksi.\n\nChemical Control\nGunakan semprotan fungisida berbahan aktif mandipropamid, klorotalonil, fluazinam, mancozeb untuk memerangi penyakit busuk daun. Fungisida secara umum hanya diperlukan jika penyakit muncul ketika hujan mungkin terjadi dalam setahun atau irigasi berlebihan dilakukan'    
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Tomato Leaf Mold':
                    treatment = 'Organic Control\nPerlakuan benih dengan air panas (25 menit pada suhu 50 derajat celcius) dianjurkan untuk menghindari patogen pada benih. Jamur Acremonium strictum, Dicyma pulvinata, Trichoderma harzianum atau T. viride dan Trichothecium roseum merupakan jamur antagonis terhadap M. fulva dan dapat digunakan untuk mengurangi penyebarannya. Dalam uji coba di rumah kaca, pertumbuhan M. fulva pada tomat dihambat oleh A. strictum, Trichoderma viride strain 3 dan T. roseum masing-masing sebesar 53, 66, dan 84%. Dalam skala kecil, sari apel, bawang putih atau semprotan susu dan campuran cuka dapat digunakan untuk mengobati jamur.\n\nChemical Control\nPemberian harus dilakukan sebelum infeksi ketika kondisi lingkungan optimal untuk perkembangan penyakit. Senyawa yang direkomendasikan untuk penggunaan di lapangan adalah formulasi chlorothalonil, maneb, mancozeb, dan tembaga. Untuk rumah kaca, difenokonazol, mandipropamid, simboksanil, famoksadon, dan siprodinil sangat direkomendasikan.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                elif predicted_class == 'Tomato Mosaic Virus':
                    treatment = 'Singkirkan tanaman yang terinfeksi, termasuk akarnya, Buang juga tanaman yang berada di dekat tanaman yang terkena. Seperti semua virus, mosaik tidak dapat disembuhkan - meskipun terkadang mosaik hanya membuat daun berpola menarik tanpa mengurangi kesegaran tanaman secara signifikan.'
                    trsource = 'https://bonide.com/disease/mosaic-viruses/#:~:text=Remove%20any%20infected%20plants%2C%20including,significantly%20reducing%20a%20plant%27s%20vigor.'
                elif predicted_class == 'Tomato Septoria Leaf Spot':
                    treatment = 'Cara Mengendalikan Bercak Daun Septoria: Saat bercak daun septoria muncul pada tomat, segera lakukan penanganan. Buang daun bagian bawah yang terinfeksi untuk membatasi penyebaran ke cabang yang menghasilkan buah. Kemudian beralihlah ke perawatan yang efektif seperti fungisida untuk melindungi jaringan yang sehat.'    
                    trsource = 'https://www.gardentech.com/disease/septoria-leaf-spot#:~:text=How%20to%20Control%20Septoria%20Leaf,fungicides%20to%20protect%20healthy%20tissue.'
                elif predicted_class == 'Tomato Target Spot':
                    treatment = 'Solusi utama yang digunakan untuk menangani bercak target pada tomat adalah penggunaan fungisida secara teratur. Pemberian harus dimulai sebelum gejala muncul ketika kondisi memungkinkan untuk terjadinya infeksi dan perkembangan penyakit. Fungisida perlu diberikan secara berkala (biasanya setiap 10 hingga 14 hari) tergantung pada petunjuk label produk yang digunakan.'
                    trsource = 'https://www.vegetables.bayer.com/ca/en-ca/resources/agronomic-spotlights/target-spot-of-tomato.html#:~:text=The%20primary%20strategy%20used%20to,for%20infection%20and%20disease%20development.'
                elif predicted_class == 'Tomato Two-Spotted Spider Mite':
                    treatment = 'Campurkan sabun cuci piring cair dan air adalah cara yang dapat dilakukan sendiri untuk mengatasi tungau laba-laba yang invasif karena sabun akan menempel dan membuat mereka mati kehabisan napas. Campurkan satu liter air hangat dengan satu sendok teh sabun cuci piring cair, aduk larutan, dan tuangkan ke dalam botol semprot.'
                    trsource = 'https://www.masterclass.com/articles/spider-mites-on-plants'
                elif predicted_class == 'Tomato Yellow Leaf Curl Virus':
                    treatment = 'Organic Control\nTidak ada pengobatan untuk melawan TYLCV. Kendalikan populasi lalat putih untuk menghindari infeksi virus.\n\nChemical Control\nSetelah terinfeksi virus, tidak ada pengobatan untuk mengatasi infeksi. Kendalikan populasi lalat putih untuk menghindari infeksi virus. Insektisida dari keluarga piretroid yang digunakan sebagai pembasah tanah atau penyemprot selama tahap pembibitan dapat mengurangi populasi lalat putih. Namun, penggunaan yang berlebihan dapat meningkatkan perkembangan resistensi pada populasi lalat putih.'
                    trsource = 'https://plantix.net/en/library/plant-diseases/'
                else:
                    treatment = 'No specific treatment available'
                    trsource = '-'

                # Return the classification result to the user
                return render(request, 'home.html', {
                    'form': form,
                    'uploaded_image': uploaded_image,
                    'predicted_class_index':predicted_class_index,
                    'predicted_class': predicted_class,
                    'probability': probability,
                    'treatment': treatment,
                    'trsource' : trsource
                })
        else:
            form = PlantImageForm()
    else:
        return render(request, 'home.html', {'form': form})

    return render(request, 'home.html', {'form': form})

def clear_results(request):
    if request.method == 'POST':
        # Clear the classification results
        return render(request, 'home.html')

#Display the 2 videos
def index(request):
    return render(request, 'home.html')

#Every time you call the phone and laptop camera method gets frame
#More info found in camera.py
def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#Method for laptop camera
def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera()),
                    #video type
					content_type='multipart/x-mixed-replace; boundary=frame')

#Method for phone camera
def webcam_feed(request):
	return StreamingHttpResponse(gen(IPWebCam()),
                    #video type
					content_type='multipart/x-mixed-replace; boundary=frame')

def capture_image_from_camera():
    # Initialize the camera capture
    cap = cv2.VideoCapture(0)

    # Check if the camera capture is successfully opened
    if not cap.isOpened():
        # Handle error if capturing image from the camera failed
        # Return a default image path or raise an exception
        return ''  # Update with appropriate handling

    try:
        # Capture image from the camera
        ret, frame = cap.read()

        # Save the captured image temporarily
        img_path = os.path.join(settings.MEDIA_ROOT, 'captured_image.jpg')
        cv2.imwrite(img_path, frame)

        # Release the camera capture
        cap.release()

        return img_path
    except Exception as e:
        # Handle exception if there was an error with capturing image from the camera
        # Return a default image path or raise an exception
        return ''  # Update with appropriate handling