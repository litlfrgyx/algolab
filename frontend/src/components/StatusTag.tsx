import type { ExperimentStatus } from '../types'
import { Tag } from './ui'

export function StatusTag({ status, done, total }: { status: ExperimentStatus; done?: number; total?: number }) {
  switch (status) {
    case 'done': return <Tag tone="ok">dokončený</Tag>
    case 'running': return <Tag tone="accent">beží{total ? ` ${done ?? 0} z ${total}` : ''}</Tag>
    case 'failed': return <Tag tone="bad">zlyhal</Tag>
    case 'cancelled': return <Tag tone="warn">prerušený</Tag>
    default: return <Tag>nespustený</Tag>
  }
}
