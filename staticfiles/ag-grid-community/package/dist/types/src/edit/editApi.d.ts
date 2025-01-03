import type { StartEditingCellParams } from '../api/gridApi';
import type { BeanCollection } from '../context/context';
import type { GetCellEditorInstancesParams, ICellEditor } from '../interfaces/iCellEditor';
import type { CellPosition } from '../interfaces/iCellPosition';
export declare function undoCellEditing(beans: BeanCollection): void;
export declare function redoCellEditing(beans: BeanCollection): void;
export declare function getCellEditorInstances<TData = any>(beans: BeanCollection, params?: GetCellEditorInstancesParams<TData>): ICellEditor[];
export declare function getEditingCells(beans: BeanCollection): CellPosition[];
export declare function stopEditing(beans: BeanCollection, cancel?: boolean): void;
export declare function startEditingCell(beans: BeanCollection, params: StartEditingCellParams): void;
export declare function getCurrentUndoSize(beans: BeanCollection): number;
export declare function getCurrentRedoSize(beans: BeanCollection): number;
