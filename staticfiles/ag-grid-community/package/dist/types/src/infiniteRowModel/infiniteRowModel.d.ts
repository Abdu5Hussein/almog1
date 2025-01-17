import type { NamedBean } from '../context/bean';
import { BeanStub } from '../context/beanStub';
import type { RowNode } from '../entities/rowNode';
import type { IDatasource } from '../interfaces/iDatasource';
import type { IRowModel, RowBounds, RowModelType } from '../interfaces/iRowModel';
export declare class InfiniteRowModel extends BeanStub implements NamedBean, IRowModel {
    beanName: "rowModel";
    private infiniteCache;
    private datasource;
    private rowHeight;
    private cacheParams;
    getRowBounds(index: number): RowBounds;
    ensureRowHeightsValid(): boolean;
    postConstruct(): void;
    start(): void;
    destroy(): void;
    private destroyDatasource;
    private addEventListeners;
    private onColumnEverything;
    getType(): RowModelType;
    setDatasource(datasource: IDatasource | undefined): void;
    isEmpty(): boolean;
    isRowsToRender(): boolean;
    getNodesInRangeForSelection(firstInRange: RowNode, lastInRange: RowNode): RowNode[];
    private reset;
    private dispatchModelUpdatedEvent;
    private resetCache;
    private updateRowHeights;
    private destroyCache;
    getRow(rowIndex: number): RowNode | undefined;
    getRowNode(id: string): RowNode | undefined;
    forEachNode(callback: (rowNode: RowNode, index: number) => void): void;
    getTopLevelRowCount(): number;
    getTopLevelRowDisplayedIndex(topLevelIndex: number): number;
    getRowIndexAtPixel(pixel: number): number;
    getRowCount(): number;
    isRowPresent(rowNode: RowNode): boolean;
    refreshCache(): void;
    purgeCache(): void;
    isLastRowIndexKnown(): boolean;
    setRowCount(rowCount: number, lastRowIndexKnown?: boolean): void;
}
