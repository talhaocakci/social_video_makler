#!/usr/bin/env python3
"""Authored, source-bound pilot. Local preview only; no upload or model API."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'work/reading-teacher-hotel'

def teacher(key, text, sentence=1, focus='', title='', body='', note='', diagram='', refs=()):
    return dict(kind='teacher', key=key, text=text, sentence=sentence, focus=focus,
                title=title, body=body, note=note, diagram=diagram, pedagogy_refs=list(refs))

def read(i):
    return dict(kind='reading', sentence=i)

def pause(key, sentence, focus, title, body):
    return dict(kind='pause', key=key, sentence=sentence, focus=focus, title=title,
                body=body, duration=4, note='Cevabı sesli söyle.', diagram='')

def main():
    variants = [
      dict(id='01-close-reading', title='Pause & notice', subtitle='Sentence-by-sentence coaching',
           treatment='paper', voice_rate=159, scenes=[
        teacher('a-intro', 'Bir otel rezervasyonu yapıyoruz. Önce Sarah’nın neye ihtiyacı olduğunu dinleyelim. Sonra birkaç küçük ayrıntıya birlikte bakalım.', 0, title='Bir rezervasyon, birkaç önemli ayrıntı', body='Dinle → Fark et → Yeniden kullan'),
        read(0), read(1),
        teacher('a-available', 'Burada bir duralım. Altını çizdiğimiz sözcük, bu tarihler için müsait, yani rezerve edilebilir anlamına geliyor. Ama dikkat: Sarah henüz sadece soruyor. Odanın gerçekten müsait olduğu daha doğrulanmadı.', 1, 'available', 'available', 'Bu tarihler için müsait; rezerve edilebilir.', 'Sormak, onay almak değildir.', refs=['s000001.word.01']),
        teacher('a-whether', 'Bir de sorunun cümleye nasıl yerleştiğine bak. Özne önce, fiil sonra geliyor. Çünkü soruyu doğrudan sormuyoruz; Sarah’nın ne sorduğunu aktarıyoruz.', 1, 'whether a room is available', 'Soruyu cümlenin içine yerleştir', 'Doğrudan soru → Aktarılan soru', diagram='question', refs=['s000001.grammar.01']),
        read(2),
        teacher('a-readback', 'Görevli burada bilgileri sadece okumuyor; kontrol edilebilsin diye sesli olarak tekrar okuyor. Tarihler, oda türü, toplam fiyat. Böylece Sarah bir yanlışlık varsa fark edebilir.', 2, 'reads back', 'reads back', 'Kontrol için bilgileri sesli tekrar okur.', 'Tarihler • Oda türü • Toplam fiyat', 'confirmation', ['s000002.word.01']),
        read(3),
        teacher('a-if', 'Buradaki kısa sözcük de önemli. Bu kez bir koşul kurmuyor; Sarah’nın iptal edip edemeyeceğini sorduğunu aktarıyor. Özne yine yardımcı fiilden önce geliyor.', 3, 'if she can cancel', 'if = whether', 'İptal edip edemeyeceğini soruyor.', 'Buradaki if, bir koşul başlatmıyor.', 'embedded', ['s000003.grammar.01']),
        read(4),
        teacher('a-end', 'Sonunda kaydettiği belge, rezervasyonun onayı. İptalin onayı değil. Şimdi üç hareketi düşün: müsaitliği sor, bilgileri kontrol et, onayı sakla. Hikâyenin akışı bu.', 4, 'confirmation', 'confirmation', 'Rezervasyonun kesinleştiğini gösteren kayıt.', 'Oda bul → Kontrol et → Onayı sakla', 'confirmation', ['s000004.word.01']),
      ]),
      dict(id='02-story-first', title='Story first', subtitle='Listen through, then unpack the meaning',
           treatment='cinema', voice_rate=167, scenes=[
        teacher('b-intro', 'Bu kez hikâyeyi bölmeden dinleyelim. Her kelimeyi çözmeye çalışma. Sarah’nın rezervasyonu nasıl tamamladığını takip etmen yeterli.', 0, title='Önce hikâyenin tamamı', body='Sarah rezervasyonu nasıl tamamlıyor?'),
        *[read(i) for i in range(5)],
        teacher('b-return', 'Şimdi, iki ayrıntıyı yakalayalım. İlkinde Sarah henüz oda bulmuş değil. Bir soru soruyor. Şu cümleyi yeniden dinle.', 1, title='Bir soruyla bir onay aynı şey mi?', body='Müsaitlik sorusu → Henüz onay yok', refs=['s000001.word.01']),
        read(1),
        teacher('b-available', 'Vurgulanan kelime, kullanılabilecek ya da rezerve edilebilecek anlamında. Burada otel odası için kullanılmış. Sarah’nın tarihlerinde boş oda var mı? Öğrenmek istediği bu.', 1, 'available', 'available', 'Kullanılabilir; burada rezerve edilebilir.', 'Anlamı, otel odası bağlamında düşün.', refs=['s000001.word.01']),
        read(2),
        teacher('b-readback', 'İşte kontrol anı. Görevli kaydettiği bilgileri Sarah’ya tekrar okuyor. Sen telefonda bir tarih söylesen, karşındaki kişi de doğrulamak için onu sana tekrar okusa, aynı hareket olurdu.', 2, 'reads back', 'reads back', 'Karşı taraf kontrol edebilsin diye tekrar okur.', 'Bu ek örnek aynı kontrol işlevini gösterir.', 'confirmation', ['s000002.word.01']),
        teacher('b-replay', 'Bu anlamları şimdi hikâyenin içine geri koyalım. Son iki cümlede iptal koşulunu ve Sarah’nın sakladığı belgeyi takip et.', 3, title='Anlamı yeniden bağlama yerleştir', body='İptal koşulu → Rezervasyon onayı'),
        read(3), read(4),
        teacher('b-end', 'Sarah rezervasyonu iptal etmiyor. İptal koşulunu öğreniyor ve rezervasyon onayını saklıyor. Kelimeleri tek tek çevirmekten çok, kimin ne yaptığını izlemek burada işimizi kolaylaştırıyor.', 4, 'confirmation', 'Hikâyenin sonucu', 'Rezervasyon yapıldı. İptal edilmedi.', 'confirmation → rezervasyon onayı', 'confirmation', ['s000003.word.01', 's000004.word.01']),
      ]),
      dict(id='03-predict-recall', title='Think & answer', subtitle='Notice, predict, then test your understanding',
           treatment='workshop', voice_rate=162, scenes=[
        teacher('c-intro', 'Bu kez biraz da sen katıl. Kısa bir bölüm dinleyeceğiz; ardından anlamı birlikte kontrol edeceğiz. Hazırsan Sarah’nın telefon görüşmesine girelim.', 0, title='Dinle. Düşün. Cevapla.', body='Küçük bir rezervasyon görevi'),
        read(0), read(1),
        teacher('c-question', 'Sence bu cümleden odanın kesin olarak müsait olduğunu anlayabilir miyiz? Yoksa Sarah henüz bunu mu soruyor? Birkaç saniye düşün.', 1, 'available', 'Oda kesin olarak müsait mi?', 'A · Evet, onaylandı.\nB · Hayır, Sarah henüz soruyor.', refs=['s000001.word.01']),
        pause('c-think', 1, 'available', 'Hangisi?', 'A · Onaylandı.\nB · Henüz soruluyor.'),
        teacher('c-answer', 'Cevap ikinci seçenek. Sarah kendi tarihleri için oda olup olmadığını soruyor. Soru, tek başına bir onay değil. Şimdi görevlinin ne yaptığını dinleyelim.', 1, 'available', 'B · Henüz soruluyor', 'Müsaitlik sorusu, rezervasyon onayı değildir.', refs=['s000001.word.01']),
        read(2),
        teacher('c-readback', 'Görevli tarihleri, oda türünü ve toplam fiyatı kontrol için tekrar okuyor. Altı çizili ifadeyi bu hareketle hatırla: bilgiyi kaydettin, sonra karşı tarafa sesli geri okudun.', 2, 'reads back', 'reads back', 'Kaydedilen bilgi → Sesli tekrar → Kontrol', diagram='confirmation', refs=['s000002.word.01']),
        read(3),
        teacher('c-if', 'Buradaki yapıyı bir önceki soruyla karşılaştır. İkisi de birinin ne sorduğunu aktarıyor. Bu cümlede de özne önce, yardımcı fiil sonra. Şimdi hikâyenin sonuna bakalım.', 3, 'if she can cancel', 'İki dolaylı soru', 'whether a room is available\nif she can cancel', 'Özne → Fiil / yardımcı fiil', 'embedded', ['s000001.grammar.01','s000003.grammar.01']),
        read(4),
        teacher('c-final-question', 'Son bir kontrol. Sarah’nın sakladığı belge neyi doğruluyor: rezervasyonun yapıldığını mı, iptal edildiğini mi? Cevabını sesli söyle.', 4, 'confirmation', 'Bu belge neyin onayı?', 'Rezervasyon mu? İptal mi?', refs=['s000004.word.01']),
        pause('c-recall', 4, 'confirmation', 'Bu belge neyin onayı?', 'Rezervasyon mu? İptal mi?'),
        teacher('c-end', 'Rezervasyonun yapıldığını. Buradaki onay, iptali değil rezervasyonu doğruluyor. Bir rezervasyon görüşmesinde de aynı sırayı izleyebilirsin: müsaitliği sor, bilgileri kontrol et, onayı sakla.', 4, 'confirmation', 'Rezervasyon onayı', 'Müsaitliği sor → Kontrol et → Onayı sakla', diagram='confirmation', refs=['s000004.word.01']),
      ]),
    ]
    raw=json.loads((WORK/'source/reading.json').read_text())
    pedagogic=json.loads((WORK/'source/pedagogy.json').read_text())
    doc=dict(schema_version=1, asset_type='reading_teacher_pilot', source_id=raw['content_id'],
             source_revision=raw['updated_at'], source_text_sha256=pedagogic['head']['source_hash'],
             source_pedagogy_checksum=pedagogic['head']['bundle_checksum'], target_language='en',
             guiding_language='tr', cefr='B1', scope='entire five-sentence reading in each variant',
             teacher_audio=dict(engine='macOS Speech Synthesis', voice='Yelda', language='tr-TR',
                                provenance='local synthetic prototype', human_audition=False),
             variants=variants)
    WORK.mkdir(parents=True,exist_ok=True)
    (WORK/'lesson.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    print('Authored three variants; no source mutation or publication.')

if __name__=='__main__': main()
