<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// Props 定义
const props = defineProps<{
  config: {
    title?: string
    refresh_interval?: number
  }
  allowRefresh?: boolean
  api?: {
    get: (path: string) => Promise<any>
  }
}>()

// 状态
const loading = ref(false)
const stats = ref({
  total: 0,
  active: 0,
  completed: 0,
  pending: 0
})

let refreshTimer: number | null = null

// 加载统计数据
async function loadStats() {
  if (!props.api) return
  
  loading.value = true
  try {
    const data = await props.api.get('plugin/Seedkeeper/stats')
    stats.value = data || { total: 0, active: 0, completed: 0, pending: 0 }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算进度百分比
function getProgress() {
  if (!stats.value.total) return 0
  return Math.round((stats.value.active / stats.value.total) * 100)
}

onMounted(() => {
  loadStats()
  
  // 自动刷新
  const interval = props.config?.refresh_interval || 30
  if (props.allowRefresh && interval > 0) {
    refreshTimer = window.setInterval(loadStats, interval * 1000)
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<template>
  <v-card class="seedkeeper-dashboard" height="100%">
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon color="success" class="mr-2">mdi-seed</v-icon>
        <span>{{ config?.title || 'SeedKeeper' }}</span>
      </div>
      <v-btn
        v-if="allowRefresh"
        icon
        size="small"
        variant="text"
        :loading="loading"
        @click="loadStats"
      >
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <!-- 进度条 -->
      <div class="mb-3">
        <div class="d-flex justify-space-between text-caption mb-1">
          <span>做种进度</span>
          <span>{{ stats.active }} / {{ stats.total }}</span>
        </div>
        <v-progress-linear
          :model-value="getProgress()"
          color="success"
          height="8"
          rounded
        />
      </div>
      
      <!-- 统计数字 -->
      <v-row dense>
        <v-col cols="4">
          <div class="text-center">
            <div class="text-h5 text-success">{{ stats.active }}</div>
            <div class="text-caption text-grey">做种中</div>
          </div>
        </v-col>
        <v-col cols="4">
          <div class="text-center">
            <div class="text-h5 text-info">{{ stats.completed }}</div>
            <div class="text-caption text-grey">已完成</div>
          </div>
        </v-col>
        <v-col cols="4">
          <div class="text-center">
            <div class="text-h5 text-warning">{{ stats.pending }}</div>
            <div class="text-caption text-grey">等待中</div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped>
.seedkeeper-dashboard {
  background: rgba(var(--v-theme-surface), 0.8) !important;
}
</style>
