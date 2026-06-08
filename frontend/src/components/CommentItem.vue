<template>
  <div class="comment-item">
    <div class="comment-header">
      <a v-if="comment.home_page" :href="comment.home_page" target="_blank">{{ comment.author }}</a>
      <span v-else>{{ comment.author }}</span>
      <span class="date">{{ new Date(comment.created_at).toLocaleString() }}</span>
    </div>
    <div class="comment-text" v-html="comment.text"></div>
    <div v-if="comment.file">
      <img v-if="isImage(comment.file)" :src="getFileUrl(comment.file)" class="thumb" @click="onLightbox(getFileUrl(comment.file))" />
      <a v-else :href="getFileUrl(comment.file)" target="_blank">file</a>
    </div>
    <button @click="onReply(comment.id)">Ответить</button>
    <span v-if="replyTo === comment.id" class="reply-indicator"> Отвечаешь на этот комментарий</span>
    <div v-if="comment.replies && comment.replies.length" class="nested-replies">
      <CommentItem
        v-for="r in comment.replies"
        :key="r.id"
        :comment="r"
        :replyTo="replyTo"
        @reply="onReply"
        @lightbox="onLightbox"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['comment','replyTo'])
const emit = defineEmits(['reply','lightbox'])

const onReply = (id) => emit('reply', id)
const onLightbox = (url) => emit('lightbox', url)

const isImage = (url) => /\.(jpg|jpeg|gif|png)$/i.test(url)
const getFileUrl = (url) => {
    if (!url) return null
    if (url.startsWith('http')) return url
    return `http://127.0.0.1:8000${url}`
}
</script>

<style scoped>
.comment-item{
    padding: 10px;
    border-left: 3px solid #e0e7ff;
    margin-top: 8px;
    background: #f9fafb;
    border-radius: 6px;
}

.comment-header {
    display: fles;
    gap: 12px;
    margin-bottom: 6px;
    font-size: 13px;
}
.comment-header a { color: #4f46e5; font-weight: 600;}
.comment-header span:first-child { font-weight: 600; color: #4f46e5;}
.date { color: #999; }
.thumb {
  width: 80px;
  height: auto;
  cursor: pointer;
  border-radius: 4px;
  margin-top: 6px;
}
button{
    margin-top: 6px;
    padding: 3px 10px;
    background: #e0e7ff;
    border: none;
    border-radius: 6px;
    color: #4f46e5;
    font-size: 12px;
    cursor: pointer;
}
.reply-indicator{ color:#4f46e5; font-size: 12px; margin-left: 8px; }
.nested-replies { margin-left: 20px; }
</style>