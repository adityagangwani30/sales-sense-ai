import type { TopProduct } from '@/lib/dashboard-types'
import { formatCurrency, formatNumber } from '@/lib/formatters'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface TopProductsTableProps {
  products: TopProduct[]
}

export function TopProductsTable({ products }: TopProductsTableProps) {
  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground">Product Revenue</h2>
        <p className="text-sm text-foreground/60 mt-1">
          Top performing products by revenue and order count.
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <TableHead className="font-semibold text-foreground/70">Product</TableHead>
            <TableHead className="text-right font-semibold text-foreground/70">Orders</TableHead>
            <TableHead className="text-right font-semibold text-foreground/70">Revenue</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.slice(0, 8).map((product) => (
            <TableRow key={product.product_name} className="hover:bg-background/50 border-border/60">
              <TableCell className="max-w-[260px] text-wrap font-medium text-foreground py-3">
                {product.product_name}
              </TableCell>
              <TableCell className="text-right text-foreground/70 py-3">
                {formatNumber(product.order_count)}
              </TableCell>
              <TableCell className="text-right font-semibold text-foreground py-3">
                {formatCurrency(product.total_revenue)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  )
}
