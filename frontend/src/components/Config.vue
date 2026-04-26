<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

// Props 定义
const props = defineProps<{
  initialConfig: {
    enabled: boolean
    auto_seed: boolean
    strategy: string
    min_ratio: number
    max_ratio: number
    seed_time_limit: number
    remove_on_limit: boolean
    downloaders: string[]
  }
  api: any
}>()

const emit = defineEmits(['save', 'close', 'switch'])

// 本地配置副本
const config = ref({
  enabled: false,
  auto_seed: true,
  strategy: 'ratio',
  min_ratio: 1.0,
  max_ratio: 5.0,
  seed_time_limit: 0,
  remove_on_limit: false,
  downloaders: [] as string[]
})

// 策略选项
const strategyOptions = [
  { title: '按分享率', value: 'ratio', icon: 'mdi-percent' },
  { title: '按做种时间', value: 'seedtime', icon: 'mdi-clock-outline' },
  { title: '手动管理', value: 'manual', icon: 'mdi-hand-pointing-up' }
]

// 下载器选项
const downloaderOptions = [
  { title: '全部下载器', value: '' },
  { title: 'qBittorrent', value: 'qbittorrent' },
  { title: 'Transmission', value: 'transmission' }
]

// 初始化配置
onMounted(() => {
  if (props.initialConfig) {
    config.value = { ...props.initialConfig }
  }
})

// 保存配置
function saveConfig() {
  emit('save', config.value)
}

// 切换到任务页面
function goToPage() {
  emit('switch')
}

// 重置为默认值
function resetConfig() {
  config.value = {
    enabled: false,
    auto_seed: true,
    strategy: 'ratio',
    min_ratio: 1.0,
    max_ratio: 5.0,
    seed_time_limit: 0,
    remove_on_limit: false,
    downloaders: []
  }
}
</script>

<template>
  <div class="seedkeeper-config pa-4">
    <div class="d-flex align-center mb-4">
      <v-icon size="28" class="mr-2" color="primary">mdi-seed</v-icon>
      <span class="text-h6">SeedKeeper 配置</span>
    </div>

    <v-card class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon class="mr-2">mdi-toggle-switch</v-icon>
        基础设置
      </v-card-title>
      <v-card-text>
        <v-switch
          v-model="config.enabled"
          label="启用插件"
          color="primary"
          hide-details
          class="mb-2"
        />
        <v-switch
          v-model="config.auto_seed"
          label="自动做种"
          color="success"
          hint="下载完成后自动开始做种"
          persistent-hint
          hide-details
        />
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon class="mr-2">mdi-strategy</v-icon>
        做种策略
      </v-card-title>
      <v-card-text>
        <v-btn-toggle
          v-model="config.strategy"
          mandatory
          color="primary"
          class="mb-4"
        >
          <v-btn value="ratio" size="small">
            <v-icon start>mdi-percent</v-icon>
            按分享率
          </v-btn>
          <v-btn value="seedtime" size="small">
            <v-icon start>mdi-clock-outline</v-icon>
            按做种时间
          </v-btn>
          <v-btn value="manual" size="small">
            <v-icon start>mdi-hand-pointing-up</v-icon>
            手动管理
          </v-btn>
        </v-btn-toggle>

        <!-- 分享率设置 -->
        <template v-if="config.strategy === 'ratio'">
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model.number="config.min_ratio"
                label="最小分享率"
                type="number"
                step="0.1"
                min="0"
                hint="达到此分享率后开始计算"
                persistent-hint
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model.number="config.max_ratio"
                label="最大分享率"
                type="number"
                step="0.1"
                min="0"
                hint="达到此分享率后自动处理"
                persistent-hint
                variant="outlined"
                density="compact"
              />
            </v-col>
          </v-row>
        </template>

        <!-- 做种时间设置 -->
        <template v-if="config.strategy === 'seedtime'">
          <v-text-field
            v-model.number="config.seed_time_limit"
            label="做种时间限制（小时）"
            type="number"
            min="0"
            hint="0 表示不做限制"
            persistent-hint
            variant="outlined"
            density="compact"
            class="max-width-300"
          />
        </template>

        <!-- 手动模式提示 -->
        <v-alert
          v-if="config.strategy === 'manual'"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-2"
        >
          手动模式下，插件不会自动处理任务，需要您在任务列表中手动操作
        </v-alert>
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon class="mr-2">mdi-download</v-icon>
        完成后处理
      </v-card-title>
      <v-card-text>
        <v-switch
          v-model="config.remove_on_limit"
          label="达到限制后删除种子"
          color="error"
          hint="关闭则只暂停做种"
          persistent-hint
          hide-details
        />
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title class="text-subtitle-1">
        <v-icon class="mr-2">mdi-server</v-icon>
        下载器选择
      </v-card-title>
      <v-card-text>
        <v-select
          v-model="config.downloaders"
          :items="downloaderOptions"
          label="选择要管理的下载器"
          multiple
          chips
          closable-chips
          variant="outlined"
          density="compact"
        />
      </v-card-text>
    </v-card>

    <!-- 操作按钮 -->
    <v-row class="mt-4">
      <v-col>
        <v-btn
          variant="text"
          @click="goToPage"
        >
          <v-icon start>mdi-arrow-left</v-icon>
          返回任务列表
        </v-btn>
      </v-col>
      <v-col class="text-right">
        <v-btn
          variant="text"
          class="mr-2"
          @click="resetConfig"
        >
          重置
        </v-btn>
        <v-btn
          color="primary"
          @click="saveConfig"
        >
          <v-icon start>mdi-content-save</v-icon>
          保存配置
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<style scoped>
.seedkeeper-config {
  background: transparent;
}

.max-width-300 {
  max-width: 300px;
}
</style>
