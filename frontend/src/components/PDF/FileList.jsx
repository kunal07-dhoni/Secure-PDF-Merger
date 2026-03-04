import React from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import FileItem from './FileItem';

export default function FileList({ files, onReorder, onRemove, onPreview }) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = files.findIndex((f) => f.index === active.id);
      const newIndex = files.findIndex((f) => f.index === over.id);
      onReorder(arrayMove(files, oldIndex, newIndex));
    }
  };

  if (files.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
          Files to Merge ({files.length})
        </h3>
        <p className="text-xs text-gray-400">Drag to reorder</p>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={files.map((f) => f.index)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {files.map((file, idx) => (
              <div key={file.index} className="relative">
                {idx > 0 && (
                  <div className="absolute -top-1 left-8 w-px h-2 bg-gray-300 dark:bg-gray-600" />
                )}
                <FileItem
                  file={file}
                  onRemove={onRemove}
                  onPreview={onPreview}
                />
              </div>
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}