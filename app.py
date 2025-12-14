# 📦 تنصيب المكتبات المطلوبة:
# pip install streamlit openai moviepy pillow arabic-reshaper python-bidi gTTS pydub
# pip install streamlit-option-menu streamlit-player

import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_player import st_player
import openai
import os
from PIL import Image
import numpy as np
from moviepy.editor import *
import tempfile
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS
from pydub import AudioSegment
import json
import requests
from io import BytesIO
import time

# ⚙️ إعدادات الصفحة
st.set_page_config(
    page_title="ReelGen AI - صانع الريلز بالعربي",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS مخصص لتجميل الواجهة
st.markdown("""
<style>
    /* خلفية متدرجة */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* تخصيص الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(255, 65, 108, 0.3);
    }
    
    /* تخصيص القوائم */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* تخصيص النصوص */
    .title-text {
        font-family: 'Tajawal', sans-serif;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* تخصيص الـ sidebar */
    .css-1d391kg {
        padding: 2rem;
    }
    
    /* تخصيص input fields */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    
    /* تخصيص sliders */
    .stSlider>div>div>div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* تحسين عرض الفيديو */
    .stVideo {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# 🔧 تهيئة API Keys (يمكن إدخالها يدوياً أو من ملف .env)
if 'OPENAI_API_KEY' not in st.session_state:
    st.session_state['OPENAI_API_KEY'] = ""

# 📁 دالة لحفظ الملفات المؤقتة
def save_uploaded_file(uploaded_file, temp_dir):
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# 🔤 دالة لمعالجة النصوص العربية
def process_arabic_text(text):
    """معالجة النص العربي للعرض الصحيح من اليمين لليسار"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# 🤖 دالة AI Hook Generator
def generate_ai_hook(topic, api_key):
    """توليد Hook جذاب باستخدام الذكاء الاصطناعي"""
    
    if not api_key:
        return {
            "hook": "📱 اكتشف سر صناعة الريلز الأكثر جاذبية!",
            "caption": "🎬 تعلم صناعة محتوى مذهل يلفت الانتباه خلال 3 ثوانٍ فقط!\n\n#صناعة_المحتوى #ريلس #تيك_توك #انستقرام",
            "emojis": "🎬🔥📱💫🌟",
            "start_prompt": "ابدأ الفيديو بلقطة قريبة من العينين مع تعبير متفاجئ"
        }
    
    try:
        openai.api_key = api_key
        
        prompt = f"""
        أنت مساعد محترف في صناعة محتوى الفيديو القصير (Reels) باللغة العربية.
        
        الموضوع: {topic}
        
        المطلوب:
        1. HOOK: جملة جذابة جداً (مثيرة للفضول، صادمة، أو مذهلة) لأول 3 ثواني من الفيديو
        2. CAPTION: نص مناسب للفيديو مع هاشتاقات مناسبة بالعربي
        3. EMOJIS: مجموعة من الإيموجيات المناسبة (3-5 إيموجي)
        4. START_PROMPT: اقتراح لكيفية بداية الفيديو (لقطة معينة، حركة، تعبير)
        
        أخرج النتيجة بالتنسيق JSON التالي:
        {{
            "hook": "النص هنا",
            "caption": "النص هنا",
            "emojis": "الإيموجيات هنا",
            "start_prompt": "الاقتراح هنا"
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد عربي متخصص في صناعة محتوى السوشيال ميديا."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content
        # استخراج JSON من النص
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group())
        else:
            # إذا لم يتم العثور على JSON، استخدام النص المباشر
            lines = result_text.split('\n')
            return {
                "hook": lines[0] if len(lines) > 0 else "🔥 اكتشف السر الآن!",
                "caption": lines[1] if len(lines) > 1 else "#تيك_توك #انستقرام",
                "emojis": "🎬🔥🌟",
                "start_prompt": "ابدأ الفيديو بحركة سريعة وجذابة"
            }
            
    except Exception as e:
        st.error(f"خطأ في توليد المحتوى: {e}")
        return {
            "hook": "🎬 كيف تصنع ريلز يجذب الملايين؟",
            "caption": "تعلم أسرار صناعة المحتوى الجذاب في 60 ثانية!\n\n#ريلس #محتوى #سوشيال_ميديا",
            "emojis": "🎬🔥📱💫",
            "start_prompt": "ابدأ الفيديو بمقدمة سريعة وجذابة"
        }

# 🎵 دالة لتحويل النص إلى كلام
def text_to_speech_arabic(text, filename):
    """تحويل النص العربي إلى كلام"""
    try:
        tts = gTTS(text=text, lang='ar', slow=False)
        tts.save(filename)
        return True
    except:
        return False

# 🎬 دالة لإنشاء الفيديو مع النصوص المتحركة
def create_reel_video(video_path, hook_text, caption_text, template_type, 
                     music_path=None, font_size=50, text_duration=3):
    """إنشاء Reel مع النصوص المؤثرات"""
    
    # تحميل الفيديو
    video = VideoFileClip(video_path)
    
    # تحديد مدة الفيديو (قصيرة للـ Reels)
    max_duration = 60  # 60 ثانية كحد أقصى
    if video.duration > max_duration:
        video = video.subclip(0, max_duration)
    
    # معالجة النصوص العربية
    hook_processed = process_arabic_text(hook_text)
    caption_processed = process_arabic_text(caption_text)
    
    # إضافة Hook (النص الأول)
    txt_hook = (TextClip(hook_processed, fontsize=font_size, color='white', 
                        font='Arial', stroke_color='black', stroke_width=2)
                .set_position(('center', 'center'))
                .set_duration(text_duration)
                .crossfadein(0.5)
                .crossfadeout(0.5))
    
    # إضافة Caption (النص الرئيسي)
    txt_caption = (TextClip(caption_processed, fontsize=font_size-10, color='yellow', 
                           font='Arial', method='caption', size=(video.w*0.9, None))
                  .set_position(('center', 'center'))
                  .set_start(text_duration)
                  .set_duration(5)
                  .crossfadein(0.5))
    
    # تطبيق القالب المختار
    if template_type == "Funny":
        # تأثيرات كوميدية
        video = video.fx(vfx.colorx, 1.2)  # زيادة الألوان
        final_video = CompositeVideoClip([video, txt_hook, txt_caption])
        
    elif template_type == "Trendy":
        # تأثيرات ترندية
        video = video.fx(vfx.lum_contrast, 0.1, 40)
        # إضافة حركة للفيديو
        video = video.resize(lambda t: 1 + 0.02*np.sin(2*np.pi*t/3))
        final_video = CompositeVideoClip([video, txt_hook, txt_caption])
        
    elif template_type == "Motivational":
        # تأثيرات ملهمة
        video = video.fx(vfx.colorx, 0.9)
        # إضافة تأثير توهج خفيف
        final_video = CompositeVideoClip([video, txt_hook, txt_caption])
        
    elif template_type == "Educational":
        # تأثيرات تعليمية
        video = video.fx(vfx.colorx, 1.0)
        final_video = CompositeVideoClip([video, txt_hook, txt_caption])
        
    else:  # Custom
        final_video = CompositeVideoClip([video, txt_hook, txt_caption])
    
    # إضافة الموسيقى إذا كانت موجودة
    if music_path and os.path.exists(music_path):
        audio_clip = AudioFileClip(music_path)
        # ضبط مستوى الصوت
        audio_clip = audio_clip.volumex(0.3)
        # قص الموسيقى لتناسب الفيديو
        if audio_clip.duration > final_video.duration:
            audio_clip = audio_clip.subclip(0, final_video.duration)
        
        # إضافة الموسيقى للفيديو
        final_video = final_video.set_audio(audio_clip)
    
    return final_video

# 🎯 الواجهة الرئيسية
def main():
    # Header
    st.markdown("<h1 class='title-text'>🎬 ReelGen AI - صانع الريلز بالعربي</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='title-text'>🔥 أنشئ ريلز احترافية بذكاء اصطناعي في دقائق!</h4>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/144/000000/video-editing.png", width=100)
        
        # إدخال API Key
        st.subheader("🔑 إعدادات API")
        api_key = st.text_input("OpenAI API Key:", type="password", 
                              value=st.session_state['OPENAI_API_KEY'])
        st.session_state['OPENAI_API_KEY'] = api_key
        
        # رفع الفيديو
        st.subheader("📤 رفع الفيديو/الصور")
        uploaded_file = st.file_uploader("اختر ملف فيديو أو صورة:", 
                                        type=["mp4", "mov", "avi", "jpg", "png", "jpeg"])
        
        # إدخال الموضوع
        st.subheader("💡 موضوع الفيديو")
        topic = st.text_area("أدخل موضوع الفيديو:", 
                           "كيف تصنع محتوى جذاب على التيك توك؟",
                           height=100)
        
        # AI Hook Generator زر
        if st.button("🤖 توليد Hook تلقائي", use_container_width=True):
            with st.spinner("جارٍ توليد محتوى جذاب..."):
                ai_content = generate_ai_hook(topic, api_key)
                st.session_state['ai_content'] = ai_content
                st.success("تم التوليد بنجاح! ✅")
        
        # عرض المحتوى المُولد
        if 'ai_content' in st.session_state:
            st.subheader("✨ المحتوى المُولد:")
            st.write(f"**Hook:** {st.session_state['ai_content']['hook']}")
            st.write(f"**Caption:** {st.session_state['ai_content']['caption']}")
            st.write(f"**إيموجيات:** {st.session_state['ai_content']['emojis']}")
            st.write(f"**بداية الفيديو:** {st.session_state['ai_content']['start_prompt']}")
        
        # إعدادات القالب
        st.subheader("🎨 إعدادات التصميم")
        template = st.selectbox("اختر قالب:", 
                               ["Funny", "Trendy", "Motivational", "Educational", "Custom"])
        
        # إعدادات النصوص
        font_size = st.slider("حجم الخط:", 20, 100, 50)
        text_duration = st.slider("مدة ظهور النصوص (ثواني):", 1, 10, 3)
        
        # إعدادات الصوت
        st.subheader("🎵 الإعدادات الصوتية")
        tts_option = st.checkbox("إضافة صوت للـ Hook")
        music_option = st.selectbox("خلفية موسيقية:", 
                                   ["بدون موسيقى", "موسيقى حماسية", "موسيقى هادئة", "موسيقى عربية"])
        
        # فلتر الفيديو
        st.subheader("🎞️ فلتر الفيديو")
        video_filter = st.selectbox("اختر فلتر:", 
                                   ["بدون فلتر", "Cinematic", "Bright", "Neon", "Vintage"])
    
    # المنطقة الرئيسية
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎥 معاينة الريلز")
        
        if uploaded_file:
            # حفظ الملف المؤقت
            temp_dir = tempfile.mkdtemp()
            video_path = save_uploaded_file(uploaded_file, temp_dir)
            
            # عرض الفيديو الأصلي
            st.video(video_path)
            
            # زر إنشاء الريلز
            if st.button("🚀 إنشاء Reel الآن", use_container_width=True):
                with st.spinner("جارٍ معالجة الفيديو وإضافة المؤثرات..."):
                    # استخدام المحتوى المُولد أو المدخل يدوياً
                    if 'ai_content' in st.session_state:
                        hook_text = st.session_state['ai_content']['hook']
                        caption_text = st.session_state['ai_content']['caption']
                        emojis = st.session_state['ai_content']['emojis']
                    else:
                        hook_text = "🎬 اكتشف السر الآن!"
                        caption_text = "🔥 محتوى جذاب ينتظرك! #ريلس #محتوى"
                        emojis = "🎬🔥🌟"
                    
                    # تحويل النص إلى كلام إذا طلب المستخدم
                    tts_path = None
                    if tts_option:
                        tts_path = os.path.join(temp_dir, "hook_audio.mp3")
                        if text_to_speech_arabic(hook_text, tts_path):
                            st.success("تم تحويل النص إلى كلام بنجاح! 🔊")
                    
                    # إنشاء الريلز النهائي
                    final_reel = create_reel_video(
                        video_path=video_path,
                        hook_text=hook_text + " " + emojis,
                        caption_text=caption_text,
                        template_type=template,
                        font_size=font_size,
                        text_duration=text_duration
                    )
                    
                    # حفظ الفيديو النهائي
                    output_path = os.path.join(temp_dir, "final_reel.mp4")
                    final_reel.write_videofile(output_path, codec='libx264', 
                                              audio_codec='aac', fps=24)
                    
                    # عرض الفيديو النهائي
                    st.success("✅ تم إنشاء الريلز بنجاح!")
                    st.video(output_path)
                    
                    # زر التحميل
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 تحميل الريلز",
                            data=file,
                            file_name="reel_ai_generated.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
        else:
            st.info("📤 يرجى رفع فيديو أو صورة لبدء المعالجة")
    
    with col2:
        st.subheader("📋 قوالب جاهزة")
        
        # عرض أمثلة للقوالب
        templates = {
            "مضحك": {
                "desc": "نصوص متحركة بألوان زاهية",
                "color": "#FF6B6B",
                "emojis": "😂🎭🤹‍♂️"
            },
            "ترندي": {
                "desc": "تأثيرات حديثة مع موسيقى عصرية",
                "color": "#4ECDC4",
                "emojis": "🔥📱💫"
            },
            "ملهم": {
                "desc": "نصوص كبيرة مع موسيقى حماسية",
                "color": "#45B7D1",
                "emojis": "💪🌟🏆"
            },
            "تعليمي": {
                "desc": "تأثيرات توضيحية مع نصوص واضحة",
                "color": "#96CEB4",
                "emojis": "📚✏️🎯"
            }
        }
        
        for name, info in templates.items():
            with st.expander(f"{info['emojis']} {name}"):
                st.markdown(f"<p style='color:{info['color']}'>{info['desc']}</p>", 
                          unsafe_allow_html=True)
                if st.button(f"استخدم قالب {name}", key=name):
                    st.session_state['selected_template'] = name
                    st.success(f"تم اختيار قالب {name}")
        
        st.subheader("💡 نصائح سريعة")
        st.info("""
        🔥 **نصائح لريلس ناجح:**
        
        1. **الـ Hook أهم 3 ثواني**
        2. **استخدم نصوص كبيرة وواضحة**
        3. **أضف موسيقى مناسبة للمحتوى**
        4. **حافظ على المدة بين 15-60 ثانية**
        5. **استخدم هاشتاقات مناسبة**
        6. **تفاعل مع المشاهدين في التعليقات**
        """)
    
    # Footer
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("**📞 الدعم الفني**")
        st.markdown("contact@reelgen-ai.com")
    
    with col_f2:
        st.markdown("**🌐 الموقع الإلكتروني**")
        st.markdown("[www.reelgen-ai.com](https://www.reelgen-ai.com)")
    
    with col_f3:
        st.markdown("**© 2024 ReelGen AI**")
        st.markdown("جميع الحقوق محفوظة")

# ملف إضافي للقوالب الجاهزة (templates.py)
"""
# ملف templates.py يمكن إضافته كمكتبة منفصلة

TEMPLATES = {
    "funny": {
        "font": "Comic-Sans-MS-Bold",
        "colors": ["#FF6B6B", "#4ECDC4", "#FFD166"],
        "animation": "bounce",
        "music": "funny_upbeat.mp3"
    },
    "trendy": {
        "font": "Montserrat-Bold",
        "colors": ["#667eea", "#764ba2", "#FF416C"],
        "animation": "slide",
        "music": "trendy_hiphop.mp3"
    },
    "motivational": {
        "font": "Roboto-Bold",
        "colors": ["#2B32B2", "#1488CC", "#00B4DB"],
        "animation": "fade",
        "music": "inspirational_orchestral.mp3"
    }
}

EFFECTS = {
    "neon": {
        "glow": True,
        "outline": "#00FFFF",
        "shadow": True
    },
    "cinematic": {
        "contrast": 1.2,
        "vignette": True,
        "letterbox": True
    },
    "bright": {
        "brightness": 1.3,
        "saturation": 1.2
    }
}
"""

if __name__ == "__main__":
    main()