import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Trash2, 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  X, 
  RefreshCw 
} from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      text: 'Merhaba! Ben Caner Holding AI Asistanıyım. Yüklediğiniz şirket belgelerine (PDF, Word, Excel, PowerPoint) dayanarak sorularınızı cevaplayabilirim veya genel konularda sohbet edebiliriz.',
      sender: 'assistant',
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Load documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);

    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/documents', {
          method: 'POST',
          body: formData,
        });
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Dosya yükleme hatası');
        }
        return await response.json();
      } catch (err) {
        console.error(`Error uploading ${file.name}:`, err);
        alert(`"${file.name}" yüklenirken hata oluştu: ${err.message}`);
        return null;
      }
    });

    await Promise.all(uploadPromises);
    setIsUploading(false);
    fetchDocuments();
  };

  const handleDeleteDocument = async (docId) => {
    if (!confirm('Bu belgeyi silmek istediğinize emin misiniz? Azure AI Search üzerindeki indeksler ve yerel dosya silinecektir.')) {
      return;
    }
    
    try {
      const response = await fetch(`/documents/${docId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchDocuments();
      } else {
        const errData = await response.json();
        alert(`Silme başarısız: ${errData.detail}`);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Belge silinirken bir hata oluştu.');
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isSending) return;

    const userMsg = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsSending(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMsg.text }),
      });

      if (response.ok) {
        const data = await response.json();
        const botMsg = {
          id: (Date.now() + 1).toString(),
          text: data.answer,
          sender: 'assistant',
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        throw new Error('API hatası');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        text: 'Bir hata oluştu. Lütfen bağlantılarınızı kontrol edip tekrar deneyin.',
        sender: 'assistant',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  // Drag & Drop event handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files);
    }
  };

  const handleClearChat = () => {
    if (confirm('Sohbet geçmişini temizlemek istiyor musunuz?')) {
      setMessages([
        {
          id: 'welcome',
          text: 'Merhaba! Ben Caner Holding AI Asistanıyım. Yüklediğiniz şirket belgelerine (PDF, Word, Excel, PowerPoint) dayanarak sorularınızı cevaplayabilirim veya genel konularda sohbet edebiliriz.',
          sender: 'assistant',
        }
      ]);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-container">
          <div className="logo-icon">
            <Sparkles size={22} />
          </div>
          <span className="logo-text">Caner Holding AI</span>
        </div>

        {/* Upload Zone */}
        <div className="section-title">Belge Yükle</div>
        <div 
          className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <UploadCloud size={32} className="upload-icon" />
          <div className="upload-text">
            {isUploading ? 'Dosya yükleniyor...' : 'Sürükleyin veya Tıklayın'}
          </div>
          <div className="upload-subtext">PDF, DOCX, XLSX, PPTX dosyaları</div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            style={{ display: 'none' }} 
            multiple
            accept=".pdf,.docx,.xlsx,.pptx"
          />
        </div>

        {/* Document List */}
        <div className="section-title" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>Kayıtlı Belgeler ({documents.length})</span>
          <button className="delete-btn" onClick={fetchDocuments} title="Listeyi Yenile">
            <RefreshCw size={12} />
          </button>
        </div>
        
        <div className="doc-list">
          {documents.length > 0 ? (
            documents.map((doc) => (
              <div key={doc.document_id} className="doc-item">
                <div className="doc-info">
                  <FileText size={16} style={{ color: '#8B5CF6', flexShrink: 0 }} />
                  <span className="doc-name" title={doc.file_name}>
                    {doc.file_name}
                  </span>
                </div>
                <button 
                  className="delete-btn"
                  onClick={() => handleDeleteDocument(doc.document_id)}
                  title="Belgeyi Sil"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          ) : (
            <div className="empty-docs">Henüz belge yüklenmedi.</div>
          )}
        </div>
      </aside>

      {/* Main Chat Container */}
      <main className="chat-container">
        {/* Chat Header */}
        <header className="chat-header">
          <div className="header-info">
            <h1>Kurumsal Yapay Zeka Asistanı</h1>
            <p>RAG + LLM Arama ve Sohbet Modülü</p>
          </div>
          <button className="clear-btn" onClick={handleClearChat}>
            <Trash2 size={14} /> Sohbeti Temizle
          </button>
        </header>

        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              <div className="avatar">
                {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-bubble">
                {msg.text}
              </div>
            </div>
          ))}
          
          {isSending && (
            <div className="message-wrapper assistant">
              <div className="avatar">
                <Bot size={18} />
              </div>
              <div className="message-bubble" style={{ minWidth: '60px' }}>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Input Container */}
        <div className="chat-input-container">
          <form className="chat-input-form" onSubmit={handleSendMessage}>
            <textarea
              className="chat-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Sorunuzu buraya yazın... (Örn: Şirket izin politikası nedir?)"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={!inputText.trim() || isSending}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
