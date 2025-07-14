import React from 'react';
import { FileText } from 'lucide-react';
import { useAquila } from '../contexts/AquilaContext';
import DocumentViewer from './DocumentViewer';
import DataModuleViewer from './DataModuleViewer';
import XMLEditor from './XMLEditor';

const MainWorkspace = () => {
  const {
    currentDocument,
    currentDataModule,
    dataModules,
    setCurrentDataModule,
    setCurrentDocument,
    documents,
  } = useAquila();

  const verbatim = currentDataModule
    ? dataModules.find(
        (dm) => dm.dmc === currentDataModule.dmc && dm.info_variant === '00'
      )
    : null;
  const ste = currentDataModule
    ? dataModules.find(
        (dm) => dm.dmc === currentDataModule.dmc && dm.info_variant === '01'
      )
    : null;

  return (
    <div className="flex-1 flex flex-col">
      {/* Main Grid - 3x2 layout */}
      <div className="aquila-main-grid">
        {/* Top Row */}
        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">Original Document</h3>
            <span className="text-xs text-aquila-text-muted">
              {currentDocument ? currentDocument.filename : 'No document loaded'}
            </span>
          </div>
          <div className="aquila-panel-content">
            <DocumentViewer document={currentDocument} />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">Verbatim DM</h3>
            <span className="text-xs text-aquila-text-muted">InfoVariant 00</span>
          </div>
          <div className="aquila-panel-content">
            <DataModuleViewer dataModule={verbatim} variant="verbatim" />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">STE DM</h3>
            <span className="text-xs text-aquila-text-muted">InfoVariant 01</span>
          </div>
          <div className="aquila-panel-content">
            <DataModuleViewer dataModule={ste} variant="ste" />
          </div>
        </div>

        {/* Bottom Row - XML Editors */}
        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">XML Editor - Verbatim</h3>
          </div>
          <div className="aquila-panel-content">
            <XMLEditor content={verbatim?.xml_content || ''} readOnly={true} />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">XML Editor - STE</h3>
          </div>
          <div className="aquila-panel-content">
            <XMLEditor content={ste?.xml_content || ''} readOnly={true} />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">Data Module List</h3>
            <div className="flex items-center gap-2">
              <button className="aquila-button-secondary text-xs px-2 py-1">
                Refresh
              </button>
              <button className="aquila-button-secondary text-xs px-2 py-1">
                Filter
              </button>
            </div>
          </div>
          <div className="aquila-panel-content overflow-auto">
            <div className="space-y-1 text-sm">
              {dataModules.length === 0 && (
                <div className="text-aquila-text-muted text-center py-8">
                  No data modules available
                </div>
              )}
              {dataModules.map((dm) => (
                <div
                  key={`${dm.dmc}_${dm.info_variant}`}
                  className={`px-2 py-1 rounded cursor-pointer ${
                    currentDataModule?.dmc === dm.dmc && currentDataModule?.info_variant === dm.info_variant
                      ? 'bg-aquila-hover'
                      : 'hover:bg-aquila-hover'
                  }`}
                  onClick={() => {
                    setCurrentDataModule(dm);
                    const doc = documents.find((d) => d.id === dm.source_document_id);
                    if (doc) setCurrentDocument(doc);
                  }}
                >
                  {dm.dmc} ({dm.info_variant}) - {dm.title}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainWorkspace;