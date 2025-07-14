import React, { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { useAquila } from '../contexts/AquilaContext';
import DocumentViewer from './DocumentViewer';
import XMLEditor from './XMLEditor';
import ProgressBar from './ProgressBar';

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

  const [verbatimText, setVerbatimText] = useState('');
  const [verbatimXML, setVerbatimXML] = useState('');
  const [steText, setSteText] = useState('');
  const [steXML, setSteXML] = useState('');
  const { updateDataModule, processingProgress } = useAquila();

  useEffect(() => {
    if (verbatim) {
      setVerbatimText(verbatim.content || '');
      setVerbatimXML(verbatim.xml_content || generateXML(verbatim, verbatim.content || ''));
    }
  }, [verbatim]);

  useEffect(() => {
    if (ste) {
      setSteText(ste.content || '');
      setSteXML(ste.xml_content || generateXML(ste, ste.content || ''));
    }
  }, [ste]);

  const generateXML = (module, content) => {
    if (!module) return '';
    return `<dataModule>\n  <identification>\n    <dmc>${module.dmc}</dmc>\n    <title>${module.title}</title>\n    <dmType>${module.dm_type}</dmType>\n    <infoVariant>${module.info_variant}</infoVariant>\n  </identification>\n  <content><![CDATA[\n${content}\n  ]]></content>\n</dataModule>`;
  };

  const extractContent = (xml) => {
    const match = xml.match(/<!\[CDATA\[(.*)\]\]>/s);
    return match ? match[1] : '';
  };

  const handleVerbatimText = (e) => {
    const val = e.target.value;
    setVerbatimText(val);
    setVerbatimXML(generateXML(verbatim, val));
  };

  const handleSteText = (e) => {
    const val = e.target.value;
    setSteText(val);
    setSteXML(generateXML(ste, val));
  };

  const handleVerbatimXml = (val) => {
    setVerbatimXML(val);
    setVerbatimText(extractContent(val));
  };

  const handleSteXml = (val) => {
    setSteXML(val);
    setSteText(extractContent(val));
  };

  const saveVerbatim = async () => {
    if (verbatim) {
      await updateDataModule(verbatim.dmc, { content: verbatimText, xml_content: verbatimXML });
    }
  };

  const saveSte = async () => {
    if (ste) {
      await updateDataModule(ste.dmc, { content: steText, xml_content: steXML });
    }
  };

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
            <button onClick={saveVerbatim} className="aquila-button-secondary text-xs ml-auto">Save</button>
          </div>
          <div className="aquila-panel-content">
            <textarea
              className="w-full h-full bg-aquila-bg border border-aquila-border rounded p-2 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-aquila-cyan"
              value={verbatimText}
              onChange={handleVerbatimText}
            />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">STE DM</h3>
            <span className="text-xs text-aquila-text-muted">InfoVariant 01</span>
            <button onClick={saveSte} className="aquila-button-secondary text-xs ml-auto">Save</button>
          </div>
          <div className="aquila-panel-content">
            <textarea
              className="w-full h-full bg-aquila-bg border border-aquila-border rounded p-2 text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-aquila-cyan"
              value={steText}
              onChange={handleSteText}
            />
          </div>
        </div>

        {/* Bottom Row - XML Editors */}
        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">XML Editor - Verbatim</h3>
          </div>
          <div className="aquila-panel-content">
            <XMLEditor content={verbatimXML} readOnly={false} onChange={handleVerbatimXml} />
          </div>
        </div>

        <div className="aquila-panel">
          <div className="aquila-panel-header">
            <h3 className="text-sm font-medium">XML Editor - STE</h3>
          </div>
          <div className="aquila-panel-content">
            <XMLEditor content={steXML} readOnly={false} onChange={handleSteXml} />
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
      <div className="p-2">
        <ProgressBar progress={processingProgress} />
      </div>
    </div>
  );
};

export default MainWorkspace;