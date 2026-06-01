<template>
  <div class="knowledge-page">
    <div class="panel">
      <h3>知识条目管理</h3>
      <div class="row">
        <input v-model="filters.keyword" placeholder="按标题/内容搜索" />
        <input v-model="filters.domain" placeholder="按领域筛选" />
        <input v-model="filters.source" placeholder="按来源筛选" />
      </div>
      <div class="actions">
        <button @click="fetchDocs">查询</button>
        <button @click="openCreate">新增条目</button>
        <button @click="resetFilters">重置</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>领域</th>
            <th>来源</th>
            <th>内容预览</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in docs" :key="doc.id">
            <td>{{ doc.id }}</td>
            <td>{{ doc.title }}</td>
            <td>{{ doc.domain || '-' }}</td>
            <td>{{ doc.source || '-' }}</td>
            <td class="preview">{{ shorten(doc.description) }}</td>
            <td>{{ formatTime(doc.created_at) }}</td>
            <td>
              <button @click="openEdit(doc)">编辑</button>
              <button class="danger" @click="removeDoc(doc.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h3>一键切块导入</h3>
      <input v-model="importForm.title" placeholder="文档标题（如：企业FAQ）" />
      <input v-model="importForm.source" placeholder="来源（如：merchant_faq）" />
      <input v-model="importForm.domain" placeholder="领域（如：售后）" />
      <input type="file" multiple accept=".txt,.md,.pdf" @change="onFileChange" />
      <textarea v-model="importForm.content" rows="10" placeholder="粘贴完整文档内容"></textarea>
      <div class="row">
        <input v-model.number="importForm.chunk_size" type="number" min="100" placeholder="chunk_size" />
        <input v-model.number="importForm.chunk_overlap" type="number" min="0" placeholder="chunk_overlap" />
      </div>
      <button :disabled="importing" @click="importKnowledge">
        {{ importing ? '导入中...' : '一键切块并导入' }}
      </button>
      <p v-if="importResult">{{ importResult }}</p>
    </div>

    <div class="panel">
      <h3>知识库改动记录</h3>
      <div class="actions">
        <button @click="fetchLogs">刷新记录</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>批次号</th>
            <th>标题</th>
            <th>来源/领域</th>
            <th>分块数</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="batch in batchLogs" :key="batch.batch_id">
            <td>{{ formatTime(batch.created_at) }}</td>
            <td>{{ batch.batch_id }}</td>
            <td>{{ batch.title || '-' }}</td>
            <td>{{ batch.source || '-' }} / {{ batch.domain || '-' }}</td>
            <td>{{ batch.imported_count }}</td>
            <td>{{ batch.undone ? '已回滚' : '有效' }}</td>
            <td>
              <button
                v-if="!batch.undone"
                class="danger"
                @click="undoBatch(batch.batch_id)"
              >
                回滚批量导入
              </button>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showEditor" class="modal">
      <div class="modal-content">
        <h3>{{ editingId ? '编辑条目' : '新增条目' }}</h3>
        <input v-model="editor.domain" placeholder="领域" />
        <input v-model="editor.title" placeholder="标题" />
        <input v-model="editor.source" placeholder="来源" />
        <textarea v-model="editor.description" rows="8" placeholder="知识内容"></textarea>
        <div class="actions">
          <button @click="saveDoc">保存</button>
          <button @click="showEditor = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { knowledgeApi } from '../../api/admin'

const docs = ref([])
const batchLogs = ref([])
const selectedFiles = ref([])
const showEditor = ref(false)
const editingId = ref(null)
const importing = ref(false)
const importResult = ref('')
const filters = ref({
  keyword: '',
  domain: '',
  source: ''
})

const editor = ref({
  domain: 'general',
  title: '',
  source: '',
  description: ''
})

const importForm = ref({
  title: '',
  source: 'manual_input',
  domain: 'general',
  content: '',
  chunk_size: 500,
  chunk_overlap: 80
})

const fetchDocs = async () => {
  const params = { limit: 500 }
  if (filters.value.keyword.trim()) params.keyword = filters.value.keyword.trim()
  if (filters.value.domain.trim()) params.domain = filters.value.domain.trim()
  if (filters.value.source.trim()) params.source = filters.value.source.trim()
  const res = await knowledgeApi.listDocs(params)
  docs.value = res.data || []
}

const fetchLogs = async () => {
  const batchRes = await knowledgeApi.listBatchChangeLogs()
  batchLogs.value = batchRes.data || []
}

const resetFilters = async () => {
  filters.value = { keyword: '', domain: '', source: '' }
  await fetchDocs()
}

const openCreate = () => {
  editingId.value = null
  editor.value = { domain: 'general', title: '', source: '', description: '' }
  showEditor.value = true
}

const openEdit = (doc) => {
  editingId.value = doc.id
  editor.value = {
    domain: doc.domain || 'general',
    title: doc.title || '',
    source: doc.source || '',
    description: doc.description || ''
  }
  showEditor.value = true
}

const saveDoc = async () => {
  if (!editor.value.title.trim()) return alert('标题不能为空')
  if (editingId.value) {
    await knowledgeApi.updateDoc(editingId.value, editor.value)
  } else {
    await knowledgeApi.createDoc(editor.value)
  }
  showEditor.value = false
  await fetchDocs()
}

const removeDoc = async (docId) => {
  if (!confirm(`确认删除条目 #${docId} 吗？`)) return
  await knowledgeApi.deleteDoc(docId)
  await fetchDocs()
}

const importKnowledge = async () => {
  if (!importForm.value.title.trim()) {
    return alert('请填写标题')
  }
  importing.value = true
  importResult.value = ''
  try {
    let res
    if (selectedFiles.value.length > 0) {
      const fd = new FormData()
      fd.append('title', importForm.value.title)
      fd.append('source', importForm.value.source)
      fd.append('domain', importForm.value.domain)
      fd.append('chunk_size', String(importForm.value.chunk_size))
      fd.append('chunk_overlap', String(importForm.value.chunk_overlap))
      selectedFiles.value.forEach((file) => fd.append('files', file))
      res = await knowledgeApi.importFilesChunked(fd)
    } else {
      if (!importForm.value.content.trim()) {
        return alert('请填写文档内容或上传文件')
      }
      res = await knowledgeApi.importChunked(importForm.value)
    }
    importResult.value = `导入成功，共写入 ${res.data.imported_count} 个知识分块。批次号：${res.data.batch_id || '-'}`
    selectedFiles.value = []
    await fetchDocs()
    await fetchLogs()
  } catch (e) {
    importResult.value = `导入失败：${e?.response?.data?.detail || e.message}`
  } finally {
    importing.value = false
  }
}

const onFileChange = (event) => {
  selectedFiles.value = Array.from(event.target.files || [])
}

const undoBatch = async (batchId) => {
  if (!confirm(`确认回滚批次 ${batchId} 吗？这会删除该次导入的所有分块。`)) return
  await knowledgeApi.undoBatchImport(batchId)
  await fetchDocs()
  await fetchLogs()
}

const formatTime = (val) => {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

const shorten = (text) => {
  const raw = (text || '').replace(/\s+/g, ' ').trim()
  if (!raw) return '-'
  if (raw.length <= 100) return raw
  return `${raw.slice(0, 100)}...`
}

onMounted(async () => {
  await fetchDocs()
  await fetchLogs()
})
</script>

<style scoped>
.knowledge-page { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { background: #fff; border: 1px solid #e3eaff; border-radius: 12px; padding: 16px; }
.actions { display: flex; gap: 8px; margin-bottom: 10px; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: left; }
.preview { max-width: 280px; }
input, textarea { width: 100%; border: 1px solid #d7deef; border-radius: 8px; padding: 8px; margin-bottom: 8px; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
button { border: none; background: #4d73ff; color: #fff; border-radius: 8px; padding: 8px 12px; cursor: pointer; }
button.danger { background: #d9534f; }
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; }
.modal-content { width: 560px; background: #fff; border-radius: 12px; padding: 16px; }
</style>
