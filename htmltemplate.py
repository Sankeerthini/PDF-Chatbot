css = '''
<style>
/* General Container Styling */
.chat-container {
    display: flex;
    flex-direction: column;
    padding: 2rem;
    margin: 0 auto;
    max-width: 900px;
    font-family: 'Arial', sans-serif;
    position: relative;
    background-color: #f8f9fa;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Chat Header */
.chat-header {
    text-align: center;
    margin-bottom: 1rem;
    font-size: 1.8rem;
    font-weight: bold;
    color: #333;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

/* Chat Message */
.chat-message {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    opacity: 0;
    animation: fadeIn 0.4s forwards ease-in-out;
}

.chat-message.user {
    justify-content: flex-end;
}

.chat-message.bot {
    justify-content: flex-start;
}

/* Avatar Styling */
.chat-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 10px;
    background: #e0e0e0;
    color: #fff;
    box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);
}

/* Chat Bubble */
.chat-bubble {
    padding: 1.2rem;
    border-radius: 20px;
    max-width: 75%;
    font-size: 1.1rem;
    line-height: 1.6;
    position: relative;
    animation: slideUp 0.4s forwards ease-in-out;
}

/* User Chat Bubble */
.chat-bubble.user {
    background: linear-gradient(135deg, #66b2ff, #0099ff);
    color: white;
    box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.3);
}

/* Bot Chat Bubble */
.chat-bubble.bot {
    background: #f1f3f5;
    color: #333;
    box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);
}

/* Animations */
@keyframes fadeIn {
    0% {
        opacity: 0;
        transform: translateY(10px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideUp {
    0% {
        transform: scale(0.95);
    }
    100% {
        transform: scale(1);
    }
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="chat-avatar">🤖</div>
    <div class="chat-bubble bot">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="chat-bubble user">{{MSG}}</div>
    <div class="chat-avatar">😊</div>
</div>
'''
