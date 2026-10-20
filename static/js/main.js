// Substitua pelo número real do WhatsApp do Ateliê (com DDD)
const NUMERO_WHATSAPP = "+5547988011949"; 

function encomendarWhatsApp(nomeProduto, codigoProduto) {
    const mensagem = `Olá! Gostaria de fazer uma encomenda do produto: *${nomeProduto}* (Código: ${codigoProduto}). Podemos combinar os detalhes?`;
    const url = `https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(mensagem)}`;
    window.open(url, '_blank');
}