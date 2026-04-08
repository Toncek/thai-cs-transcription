# Edge Cases and Conflicts

## Conflicts
- `ใต` maps to multiple outputs: ['taj', 'táj']
- `จังหวัด` maps to multiple outputs: ['džang vat', 'džangvat']
- `ทางดวน` maps to multiple outputs: ['tháng dúan', 'tháng duan']
- `พูกัน` maps to multiple outputs: ['phúkan', 'phú kan']
- `เสาอากาศ` maps to multiple outputs: ['sáu ákát', 'sau ákát']
- `ที่เขี่ยบุหรี่` maps to multiple outputs: ['thýkhyja burý', 'thý khyja burý']
- `ชั้นวางของ` maps to multiple outputs: ['čán váng khóng', 'čan váng khóng']
- `โตะ` maps to multiple outputs: ['to', 'tó']
- `นํ้าสมสายช ู` maps to multiple outputs: ['nám som sáj čú', 'nám som sájčú']
- `ขวดเกลือ` maps to multiple outputs: ['khúat klúa', 'khuat klúa']
- `ขวดพริกไทย` maps to multiple outputs: ['khuat phryk thaj', 'khúat phryk thaj']
- `กลองทิชชู` maps to multiple outputs: ['klóng thytčú', 'klóng thyt čú']
- `ถังนํ้า` maps to multiple outputs: ['thang nám', 'tháng nám']
- `นางพยาบาล` maps to multiple outputs: ['náng phajábán', 'náng pha já bán']
- `โรงพยาบาล` maps to multiple outputs: ['róng phajábán', 'róng pha já bán']
- `รถพยาบาล` maps to multiple outputs: ['rot phajábán', 'rot pha já bán']
- `การรักษาพยาบาล` maps to multiple outputs: ['kánraksá phajábán', 'kán raksá phajábán']
- `เขา` maps to multiple outputs: ['khao', 'khau']
- `เปด` maps to multiple outputs: ['pet', 'pét']
- `คันเรง` maps to multiple outputs: ['khanreng', 'khan reng']
- `อ` maps to multiple outputs: ['máj trý', 'máj džat tavá', 'máj thó', 'ó', 'máj ék', 'káran']

## Unconfirmed exceptions (< 3 occurrences)
The majority of the training set consists of words appearing 1 or 2 times. They fail the strict 3-example threshold for exceptions. They are not hardcoded into `rules.json` to prevent memorization and data leakage.
