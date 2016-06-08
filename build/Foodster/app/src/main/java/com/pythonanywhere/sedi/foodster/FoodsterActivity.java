package com.pythonanywhere.sedi.foodster;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.support.design.widget.TabLayout;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;
import com.pythonanywhere.sedi.foodster.fragments.BarcodeReaderFragment;
import com.pythonanywhere.sedi.foodster.fragments.RecipesFragment;
import com.pythonanywhere.sedi.foodster.fragments.ShoppingListFragment;
import com.pythonanywhere.sedi.foodster.models.JSONfunctions;
import com.pythonanywhere.sedi.foodster.models.ResponseWrapper;
import com.pythonanywhere.sedi.foodster.views.adapters.FoodsterPagerAdapter;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class FoodsterActivity extends AppCompatActivity
        implements BarcodeReaderFragment.OnScanButtonClickedListener{

    private FoodsterPagerAdapter foodsterPagerAdapter;
    private Toolbar toolbar;
    private TabLayout tabLayout;
    private ViewPager viewPager;

    private boolean toProccessFlag;
    private IntentResult intentResult;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        toProccessFlag = false;
        if(!checkLogin()){
            finish();
        }

        setContentView(R.layout.activity_main);

        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        viewPager = (ViewPager) findViewById(R.id.pager);
        viewPager.setOffscreenPageLimit(2);
        setupViewPager(viewPager);

        tabLayout = (TabLayout) findViewById(R.id.tab_layout);
        tabLayout.setupWithViewPager(viewPager);

    }

    private boolean checkLogin(){

        boolean flag = false;

        SharedPreferences sharedPref
                = getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
        String token
                = sharedPref.getString(getString(R.string.saved_token), getString(R.string.not_logged_status));

        if(!token.equals(getString(R.string.not_logged_status))) {
            AsyncTask task = new AsyncTask<Void, Void, Void>() {

                @Override
                protected Void doInBackground(Void... params) {
                    SharedPreferences sharedPref
                            = getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
                    String token
                            = sharedPref.getString(getString(R.string.saved_token), getString(R.string.not_logged_status));

                    ResponseWrapper rw = JSONfunctions.getWithJSONResult(getString(R.string.shopping_list_list), token);
                    if (rw.getResponseCode() != 200) {
                        SharedPreferences.Editor editor = sharedPref.edit();
                        editor.putString(getString(R.string.saved_token), getString(R.string.not_logged_status));
                        editor.commit();
                    }
                    return null;
                }
            };

            try {
                task.get(1000, TimeUnit.MILLISECONDS);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } catch (ExecutionException e) {
                e.printStackTrace();
            } catch (TimeoutException e) {
                e.printStackTrace();
            }

            token = sharedPref.getString(getString(R.string.saved_token), getString(R.string.not_logged_status));
//            try {
//                task.execute().get();
//
//            } catch (InterruptedException e) {
//                e.printStackTrace();
//            } catch (ExecutionException e) {
//                e.printStackTrace();
//            }

        }

        if(token.equals(getString(R.string.not_logged_status))){
            Intent i = new Intent(this, LoginActivity.class);
            startActivity(i);
            flag = false;
        }
        else flag = true;
        return flag;
    }

    private void setupViewPager(ViewPager viewPager){
        foodsterPagerAdapter = new FoodsterPagerAdapter(getSupportFragmentManager());
        foodsterPagerAdapter.addFragment(new ShoppingListFragment(), "Shopping list");
        foodsterPagerAdapter.addFragment(new RecipesFragment(), "Recipes");
        foodsterPagerAdapter.addFragment(new BarcodeReaderFragment(), "Barcode reader");

        viewPager.setAdapter(foodsterPagerAdapter);

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.log_out) {

            SharedPreferences sharedPref
                    = getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
            SharedPreferences.Editor editor = sharedPref.edit();
            editor.putString(getString(R.string.saved_token), getString(R.string.not_logged_status));
            editor.commit();

            Intent i = new Intent(this, LoginActivity.class);
            startActivity(i);
            finish();

            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {

        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
//        System.out.println("Request code: " + requestCode);
//        System.out.println("Result code: " + resultCode);

        toProccessFlag = resultCode == -1;
        System.out.println("Flaga ustawiona na : " + toProccessFlag);

//        BarcodeReaderFragment page;
//        do{
//            page = (BarcodeReaderFragment) getSupportFragmentManager().findFragmentByTag("android:switcher" + R.id.pager + ":" + viewPager.getCurrentItem());
//        }while(page != null);
//        page.processResult(requestCode, resultCode, intent);

//        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
//
//        if(scanningResult != null){
//            String scanContent = scanningResult.getContents();
//            String scanFormat = scanningResult.getFormatName();
//            Toast toast = Toast.makeText(getApplicationContext(),
//                    "Scan format: " + scanFormat + " ; Scan result: " + scanContent , Toast.LENGTH_LONG);
//            toast.show();
//        }
    }

    @Override
    public IntentResult askForResult() {
        return intentResult;
    }

    @Override
    public boolean checkToProccess() {
        return toProccessFlag;
    }
}
