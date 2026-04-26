<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// Props 定义
const props = defineProps<{
  api: {
    get: (path: string) => Promise<any>
    post: (path: string, data: any) => Promise<any>
  }
}>()

const emit = defineEmits(['action', 'switch', 'close'])

// 状态
const loading = ref(false)
const stats = ref({
  total: 0,
  active: 0,
  completed: 0,
  pending: 0
})
const tasks = ref<any[]>([])

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const [statsData, tasksData] = await Promise.all([
      props.api.get('plugin/Seedkeeper/stats'),
      props.api.get('plugin/Seedkeeper/tasks')
    ])
    stats.value = statsData
    tasks.value = tasksData || []
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新
function refreshTasks() {
  loadData()
}

// 恢复做种
async function resumeTask(hash: string) {
  try {
    await props.api.post('plugin/Seedkeeper/task/resume', { hash })
    await loadData()
  } catch (error) {
    console.error('恢复失败:', error)
  }
}

// 暂停做种
async function pauseTask(hash: string) {
  try {
    await props.api.post('plugin/Seedkeeper/task/pause', { hash })
    await loadData()
  } catch (error) {
    console.error('暂停失败:', error)
  }
}

// 删除种子
async function removeTask(hash: string) {
  if (!confirm('确定要删除这个种子吗？')) return
  try {
    await props.api.post('plugin/Seedkeeper/task/remove', { hash })
    await loadData()
    emit('action')
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 切换到配置页
function goToConfig() {
  emit('switch')
}

// 获取状态颜色
function getStatusColor(status: string) {
  switch (status) {
    case 'seeding': return 'success'
    case 'completed': return 'info'
    case 'paused': return 'warning'
    default: return 'grey'
  }
}

// 获取状态文本
function getStatusText(status: string) {
  switch (status) {
    case 'seeding': return '做种中'
    case 'completed': return '已完成'
    case 'paused': return '已暂停'
    default: return '未知'
  }
}

// 格式化分享率
function formatRatio(ratio: number) {
  if (!ratio && ratio !== 0) return '-'
  return ratio.toFixed(2)
}

// 格式化时间
function formatTime(hours: number) {
  if (!hours) return '-'
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d ${hours % 24}h`
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="seedkeeper-page pa-4">
    <!-- 统计卡片 -->
    <v-row class="mb-4">
      <v-col cols="3">
        <v-card color="primary" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.active }}</div>
            <div class="text-caption">做种中</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card color="success" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.completed }}</div>
            <div class="text-caption">已完成</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card color="warning" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.pending }}</div>
            <div class="text-caption">等待中</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card color="info" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-h4 font-weight-bold">{{ stats.total }}</div>
            <div class="text-caption">总任务</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 操作栏 -->
    <v-row class="mb-4 align-center">
      <v-col>
        <span class="text-subtitle-1">🌱 做种任务列表</span>
      </v-col>
      <v-col class="text-right">
        <v-btn
          color="primary"
          variant="tonal"
          size="small"
          class="mr-2"
          @click="refreshTasks"
          :loading="loading"
        >
          <v-icon>mdi-refresh</v-icon>
          刷新
        </v-btn>
        <v-btn
          color="secondary"
          variant="tonal"
          size="small"
          @click="goToConfig"
        >
          <v-icon>mdi-cog</v-icon>
          配置
        </v-btn>
      </v-col>
    </v-row>

    <!-- 任务列表 -->
    <v-card>
      <v-data-table
        :headers="[
          { title: '任务名称', key: 'name', sortable: true },
          { title: '分享率', key: 'current_ratio', align: 'center' },
          { title: '做种时间', key: 'seeding_time', align: 'center' },
          { title: '状态', key: 'status', align: 'center' },
          { title: '操作', key: 'actions', align: 'center', sortable: false }
        ]"
        :items="tasks"
        :loading="loading"
        :items-per-page="10"
        class="elevation-1"
      >
        <template #item.name="{ item }">
          <div class="text-truncate" style="max-width: 300px;">
            {{ item.name || '未知任务' }}
          </div>
        </template>

        <template #item.current_ratio="{ item }">
          <v-chip
            :color="item.current_ratio >= 1 ? 'success' : 'grey'"
            size="small"
            variant="tonal"
          >
            {{ formatRatio(item.current_ratio) }}
          </v-chip>
        </template>

        <template #item.seeding_time="{ item }">
          {{ formatTime(item.seeding_time) }}
        </template>

        <template #item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            v-if="item.status !== 'seeding'"
            icon
            size="small"
            color="success"
            variant="text"
            @click="resumeTask(item.hash)"
          >
            <v-icon>mdi-play</v-icon>
          </v-btn>
          <v-btn
            v-if="item.status === 'seeding'"
            icon
            size="small"
            color="warning"
            variant="text"
            @click="pauseTask(item.hash)"
          >
            <v-icon>mdi-pause</v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            color="error"
            variant="text"
            @click="removeTask(item.hash)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>

        <template #no-data>
          <div class="text-center pa-4 text-grey">
            <v-icon size="48" class="mb-2">mdi-seed-off</v-icon>
            <div>暂无做种任务</div>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<style scoped>
.seedkeeper-page {
  background: transparent;
}
</style>
