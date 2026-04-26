<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// Props 定义
const props = defineProps<{
  api: {
    get: (path: string) => Promise<any>
    post: (path: string, data: any) => Promise<any>
  }
  navKey?: string
  pluginId?: string
}>()

const emit = defineEmits(['action'])

// 状态
const activeTab = ref('tasks')
const loading = ref(false)
const stats = ref({
  total: 0,
  active: 0,
  completed: 0,
  pending: 0
})
const tasks = ref<any[]>([])
const config = ref({
  enabled: false,
  auto_seed: true,
  strategy: 'ratio',
  min_ratio: 1.0,
  max_ratio: 5.0,
  seed_time_limit: 0,
  remove_on_limit: false,
  downloaders: []
})

// 加载所有数据
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
function refresh() {
  loadData()
  emit('action')
}

// 保存配置
async function saveConfig(newConfig: any) {
  try {
    // 这里应该调用插件的配置保存接口
    console.log('保存配置:', newConfig)
    emit('action')
  } catch (error) {
    console.error('保存配置失败:', error)
  }
}

// 任务操作
async function resumeTask(hash: string) {
  await props.api.post('plugin/Seedkeeper/task/resume', { hash })
  await loadData()
  emit('action')
}

async function pauseTask(hash: string) {
  await props.api.post('plugin/Seedkeeper/task/pause', { hash })
  await loadData()
  emit('action')
}

async function removeTask(hash: string) {
  if (!confirm('确定要删除这个种子吗？')) return
  await props.api.post('plugin/Seedkeeper/task/remove', { hash })
  await loadData()
  emit('action')
}

function getStatusColor(status: string) {
  switch (status) {
    case 'seeding': return 'success'
    case 'completed': return 'info'
    case 'paused': return 'warning'
    default: return 'grey'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'seeding': return '做种中'
    case 'completed': return '已完成'
    case 'paused': return '已暂停'
    default: return '未知'
  }
}

function formatRatio(ratio: number) {
  if (!ratio && ratio !== 0) return '-'
  return ratio.toFixed(2)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="seedkeeper-app-page">
    <!-- 顶部导航 -->
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>
        <v-icon class="mr-2">mdi-seed</v-icon>
        SeedKeeper 做种助手
      </v-app-bar-title>
      <v-spacer />
      <v-btn icon variant="text" @click="refresh">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <!-- 统计卡片 -->
        <v-row class="mb-4">
          <v-col cols="6" sm="3">
            <v-card color="success" variant="tonal">
              <v-card-text class="text-center py-4">
                <v-icon size="32" class="mb-2">mdi-arrow-up-bold</v-icon>
                <div class="text-h4 font-weight-bold">{{ stats.active }}</div>
                <div class="text-caption">做种中</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="info" variant="tonal">
              <v-card-text class="text-center py-4">
                <v-icon size="32" class="mb-2">mdi-check-circle</v-icon>
                <div class="text-h4 font-weight-bold">{{ stats.completed }}</div>
                <div class="text-caption">已完成</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="warning" variant="tonal">
              <v-card-text class="text-center py-4">
                <v-icon size="32" class="mb-2">mdi-clock-outline</v-icon>
                <div class="text-h4 font-weight-bold">{{ stats.pending }}</div>
                <div class="text-caption">等待中</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="primary" variant="tonal">
              <v-card-text class="text-center py-4">
                <v-icon size="32" class="mb-2">mdi-folder-multiple</v-icon>
                <div class="text-h4 font-weight-bold">{{ stats.total }}</div>
                <div class="text-caption">总任务</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 标签页 -->
        <v-tabs v-model="activeTab" color="primary" class="mb-4">
          <v-tab value="tasks">
            <v-icon start>mdi-format-list-bulleted</v-icon>
            任务列表
          </v-tab>
          <v-tab value="config">
            <v-icon start>mdi-cog</v-icon>
            插件配置
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- 任务列表 -->
          <v-window-item value="tasks">
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
              >
                <template #item.name="{ item }">
                  <div class="text-truncate" style="max-width: 250px;">
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
                  <div class="text-center pa-8 text-grey">
                    <v-icon size="64" class="mb-4">mdi-seed-off</v-icon>
                    <div class="text-h6 mb-2">暂无做种任务</div>
                    <div class="text-caption">开始下载后，这里会显示做种任务</div>
                  </div>
                </template>
              </v-data-table>
            </v-card>
          </v-window-item>

          <!-- 配置页面 -->
          <v-window-item value="config">
            <v-card>
              <v-card-title class="d-flex align-center">
                <v-icon class="mr-2">mdi-cog</v-icon>
                插件配置
              </v-card-title>
              <v-card-text>
                <Config
                  :initial-config="config"
                  :api="api"
                  @save="saveConfig"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </div>
</template>

<style scoped>
.seedkeeper-app-page {
  min-height: 100vh;
  background: rgb(var(--v-theme-background));
}
</style>
