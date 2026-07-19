from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.core.config import settings
from app.services.ai.conversation_service import ConversationService


class AIService:
    """Handles communication with Azure AI Foundry."""

    def __init__(self) -> None:
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default",
        )

        self._client = OpenAI(
            base_url=settings.project_endpoint,
            api_key=token_provider,
        )

        self._conversation = ConversationService()

    def _generate_response(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        self._conversation.add_user_message(prompt)

        response = self._client.responses.create(
            model=settings.model_deployment,
            input=self._conversation.get_messages(),
        )

        assistant_response = response.output_text

        self._conversation.add_assistant_message(assistant_response)

        return assistant_response

    def chat(self, message: str) -> str:
        return self._generate_response(message)

    def rag_chat(self, rag_prompt: str, original_question: str) -> str:
        """RAG modu için özel sohbet metodu.

        Hafızaya sadece kullanıcının orijinal sorusunu ve asistanın cevabını kaydeder.
        LLM'e ise belge bağlamını içeren tam RAG prompt'unu gönderir.
        Bu sayede konuşma geçmişi gereksiz belge parçalarıyla şişmez.
        """
        self._conversation.add_user_message(original_question)

        response = self._client.responses.create(
            model=settings.model_deployment,
            input=[
                {"role": "system", "content": self._conversation.get_messages()[0]["content"]},
                *self._conversation.get_messages()[1:-1],
                {"role": "user", "content": rag_prompt},
            ],
        )

        assistant_response = response.output_text

        self._conversation.add_assistant_message(assistant_response)

        return assistant_response

    def classify(self, message: str) -> str:
        prompt = f"""
Sen bir yönlendirici yapay zekasın.
Kullanıcının mesajına bakarak aşağıdaki iki aksiyondan birini seç.

Aksiyonlar:
- rag -> Kullanıcı herhangi bir soru soruyor, bilgi istiyor, bir konu hakkında araştırma yapıyor veya bir şey öğrenmek istiyorsa. Bu VARSAYILAN aksiyondur. Emin değilsen bunu seç.
- chat -> SADECE kullanıcı selamlama (merhaba, selam, nasılsın), teşekkür, vedalaşma veya kısa günlük sohbet yapıyorsa.

Sadece tek bir kelime ile cevap ver:
rag
veya
chat

Kullanıcı:
{message}
"""

        response = self._client.chat.completions.create(
            model=settings.model_deployment,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response.choices[0].message.content.strip().lower()

    def summarize(self, text: str) -> str:
        prompt = f"Summarize the following text clearly and concisely:\n\n{text}"

        return self._generate_response(prompt)

    def extract_keywords(self, text: str) -> list[str]:
        prompt = f"""
Extract the most important keywords from the following text.
Return only comma-separated keywords.

Text:
{text}
"""

        response = self._generate_response(prompt)

        return [
            keyword.strip()
            for keyword in response.split(",")
            if keyword.strip()
        ]

    def reformulate_query(self, question: str) -> str:
        messages = self._conversation.get_messages()

        user_messages_count = sum(1 for m in messages if m["role"] == "user")
        if user_messages_count == 0:
            return question

        history_text = ""
        for m in messages:
            role_name = "Kullanıcı" if m["role"] == "user" else "Asistan" if m["role"] == "assistant" else "Sistem"
            if role_name != "Sistem":
                history_text += f"{role_name}: {m['content']}\n"

        prompt = f"""
Sana bir sohbet geçmişi ve kullanıcının sorduğu yeni bir takip sorusu verilecek.
Senin görevin, bu takip sorusunu geçmişe bakarak tek başına anlam ifade eden ve bir arama motorunda aratılabilecek detaylı bir arama sorgusuna dönüştürmektir.

Kurallar:
1. Eğer takip sorusu zaten kendi başına açık ve netse veya geçmişe bağımlı değilse, soruyu hiç değiştirmeden aynen geri döndür.
2. Eğer takip sorusu geçmişteki bir konuya ("o", "ne satılmış", "kim yapmış", "nerede", "peki ne", "ne zaman" vb. zamirlerle) atıfta bulunuyorsa, bu zamirlerin yerine geçmişteki ilgili isimleri/tarihleri koyarak soruyu açık hale getir.
3. Çıktı olarak SADECE yeniden yazılmış soruyu ver, başka hiçbir açıklama veya yorum yazma.
4. Tarihleri veya sayıları koru ve gerekiyorsa standart formatta (örneğin 2025-01-05 gibi) yaz.

Sohbet Geçmişi:
{history_text}

Takip Sorusu:
{question}

Yeniden Yazılmış Sorgu:
"""
        response = self._client.chat.completions.create(
            model=settings.model_deployment,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        reformulated = response.choices[0].message.content.strip()
        if not reformulated:
            return question
        return reformulated

