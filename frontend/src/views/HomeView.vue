<template>
  <div class="container">
    <h1>Комментарии</h1>

    <div class="form-block">
      <h2>Добавить комментарий</h2>
      <input v-model="form.username" placeholder="Username (латиница и цифры)" />
      <input v-model="form.email" placeholder="Email" />
      <input v-model="form.home_page" placeholder="Home page (необязательно)" />
      
      <div class="captcha-block">
        <img :src="captcha.image" @click="loadCaptcha" title="Обновить капчу" />
        <input v-model="form.captcha_value" placeholder="Введи капчу" />
      </div>

      <div class="tag-panel">
        <button @click="insertTag('i')">[i]</button>
        <button @click="insertTag('strong')">[strong]</button>
        <button @click="insertTag('code')">[code]</button>
        <button @click="insertTag('a')">[a]</button>
      </div>

      <textarea ref="textareaRef" v-model="form.text" placeholder="Текст комментария"></textarea>
      <input type="file" @change="onFileChange" accept=".jpg,.jpeg,.gif,.png,.txt" />

      <div class="buttons">
        <button @click="preview">Предпросмотр</button>
        <button @click="submitComment">Отправить</button>
      </div>


      <div v-if="previewText" class="preview-block">
        <h3>Предпросмотр:</h3>
        <p>{{ previewText }}</p>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="comments-block">
      <table>
        <thead>
          <tr>
            <th @click="sort('username')">Username</th>
            <th @click="sort('email')">Email</th>
            <th @click="sort('created_at')">Дата</th>
            <th>Текст</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in comments" :key="c.id">
            <td>
              <a v-if="c.home_page" :href="c.home_page" target="_blank" style="color:#4f46e5;">{{ c.author }}</a>
              <span v-else>{{ c.author }}</span>
            </td>
            <td>{{ c.email }}</td>
            <td>{{ new Date(c.created_at).toLocaleString() }}</td>
            <td>
              <span v-html="c.text"></span>
              <div v-if="c.file">
                <img v-if="isImage(c.file)" :src="getFileUrl(c.file)" class="thumb" @click="openLightbox(getFileUrl(c.file))" />
                <a v-else :href="c.file" target="_blank"> файл</a>
              </div>
              <button @click="setReply(c.id)">Ответить</button>
              <span v-if="reptyTo === c.id" style="color:#4f46e5; font-size:12px; margin-left:8px;"> Отвечаешь на этот комментарий</span>
              <div v-if="c.replies && c.replies.length" class="replies">
                CommentItem
                  v-for="r in c.replies"
                  :key="r.id"
                  :comment="r"
                  :replyTo="replyTo"
                  @reply="setReply"
                  @lightbox="openLightbox"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>


      <div class="pagination">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">←</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">→</button>
      </div>
    </div>

    <div v-if="lightboxImg" class="lightbox" @click="lightboxImg = null">
      <img :src="lightboxImg" />
    </div>
  </div>
</template>

<script setup>
import CommentItem from '../components/CommentItem.vue'
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'

const comments = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const sortField = ref('created_at')
const sortOrder = ref('desc')
const error = ref('')
const previewText = ref('')
const lightboxImg = ref(null)
const textareaRef = ref(null)

const captcha = ref({ key: '', image: '' })
const form = ref({
  username: '',
  email: '',
  home_page: '',
  text: '',
  captcha_value: '',
})
const selectedFile = ref(null)
const replyTo = ref(null)

const loadCaptcha = async () => {
  const res = await axios.get(`${API}/captcha/new/`)
  captcha.value = { key: res.data.key, image: res.data.image }
}

const loadComments = async () => {
  const res = await axios.get(`${API}/comments/`, {
    params: { page: currentPage.value, sort: sortField.value, order: sortOrder.value }
  })
  comments.value = res.data.comments
  totalPages.value = res.data.pages
}

const sort = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  loadComments()
}

const changePage = (p) => {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  loadComments()
}

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

const setReply = (id) => {
  replyTo.value = id
}

const preview = () => {
  previewText.value = form.value.text
}

const submitComment = async () => {
  error.value = ''
  const data = new FormData()
  data.append('username', form.value.username)
  data.append('email', form.value.email)
  data.append('home_page', form.value.home_page)
  data.append('text', form.value.text)
  data.append('captcha_key', captcha.value.key)
  data.append('captcha_value', form.value.captcha_value)
  if (replyTo.value) data.append('parent_id', replyTo.value)
  if (selectedFile.value) data.append('file', selectedFile.value)

  if (!form.value.username){
    error.value = 'Username обязателен'
    return
  }
  if (!/^[a-zA-Z0-9]+$/.test(form.value.username)){
    error.value = 'Username латиница и цифры'
    return
  }
  if (!form.value.email){
    error.value = 'Email обязателен'
    return
  }
  if (!/^[^@]+@[^@]+\.[^@]+$/.test(form.value.email)){
    error.value = 'неверный формат почты'
    return
  }
  if (!form.value.text){
    error.value = 'текст обязателен'
    return
  }
  if (!form.value.captcha_value){
    error.value = 'Введите каптчу'
    return
  }



  try {
    await axios.post(`${API}/comments/`, data)
    form.value = { username: '', email: '', home_page: '', text: '', captcha_value: '' }
    replyTo.value = null
    selectedFile.value = null
    await loadCaptcha()
    await loadComments()
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка'
    await loadCaptcha()
  }
}

const insertTag = (tag) => {
  const textarea = textareaRef.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = form.value.text.substring(start, end)
  const before = form.value.text.substring(0, start)
  const after = form.value.text.substring(end)
  
  if (tag === 'a') {
    const href = prompt('Введи ссылку:')
    if (!href) return
    form.value.text = `${before}<a href="${href}">${selected || href}</a>${after}`
  } else {
    form.value.text = `${before}<${tag}>${selected}</${tag}>${after}`
  }
}
const isImage = (url) => /\.(jpg|jpeg|gif|png)$/i.test(url)
const getFileUrl = (url) => {
  if (!url) return null
  if (url.startsWith('http')) return url
  return `http://127.0.0.1:8000${url}`
}
const openLightbox = (url) => {
  lightboxImg.value = url
}

// WebSocket
const connectWS = () => {
  const ws = new WebSocket('ws://127.0.0.1:8000/ws/comments/')
  ws.onmessage = (e) => {
    const comment = JSON.parse(e.data)
    comments.value.unshift(comment)
  }
  ws.onclose = () => setTimeout(connectWS, 3000)
}

onMounted(() => {
  loadCaptcha()
  loadComments()
  connectWS()
})
</script>

<style scoped>
* { box-sizing: border-box; }

.container {
  width: 100%;
  max-width: 100%;
  margin: 30px 0;
  padding: 0 60px;
  font-family: 'Segoe UI', sans-serif;
  color: #333;
}
h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #1a1a2e;
  border-bottom: 3px solid #4f46e5;
  padding-bottom: 10px;
}


code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: #e53e3e;
}

.form-block {
  background: white;
  padding: 28px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 28px;
  width: 100%;
}
h2 {
  font-size: 18px;
  margin-bottom: 18px;
  color: #1a1a2e;
}

.form-block input,
.form-block textarea {
  display: block;
  width: 100%;
  margin-bottom: 12px;
  padding: 10px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border 0.2s;
  outline: none;
}

.form-block input:focus,
.form-block textarea:focus {
  border-color: #4f46e5;
}

.form-block textarea {
  height: 120px;
  resize: vertical;
}

.captcha-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.captcha-block img {
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  height: 44px;
}

.captcha-block input {
  margin-bottom: 0 !important;
  flex: 1;
}

.tag-panel {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.tag-panel button {
  padding: 5px 12px;
  background: #f3f4f6;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  transition: background 0.2s;
}

.tag-panel button:hover {
  background: #e0e7ff;
}

.buttons {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.buttons button {
  padding: 10px 22px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.buttons button:first-child {
  background: #f3f4f6;
  color: #333;
}

.buttons button:last-child {
  background: #4f46e5;
  color: white;
}

.buttons button:hover { opacity: 0.85; }

.preview-block {
  margin-top: 14px;
  padding: 14px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 4px solid #4f46e5;
  font-size: 14px;
}

.error {
  color: #ef4444;
  margin-top: 10px;
  font-size: 14px;
}

.comments-block {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  width: 100%;
}
table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #1a1a2e;
  color: white;
}

th {
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  letter-spacing: 0.5px;
}

th:hover { background: #2d2d50; }

td {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  vertical-align: top;
}

tr:hover td { background: #fafafa; }

td:first-child { font-weight: 600; color: #4f46e5; }

.thumb {
  width: 80px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 6px;
  transition: opacity 0.2s;
}

.thumb:hover { opacity: 0.8; }

.replies {
  margin-top: 10px;
  padding-left: 14px;
  border-left: 3px solid #e0e7ff;
}

.reply {
  margin-bottom: 6px;
  font-size: 13px;
  color: #555;
  padding: 6px 10px;
  background: #f9fafb;
  border-radius: 6px;
}

.reply b { color: #4f46e5; }

td button {
  margin-top: 8px;
  padding: 4px 12px;
  background: #e0e7ff;
  border: none;
  border-radius: 6px;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

td button:hover { background: #c7d2fe; }

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
}

.pagination button {
  padding: 8px 18px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.pagination button:disabled {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

.pagination span { font-size: 14px; color: #555; }

.lightbox {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1000;
}

.lightbox img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
</style>